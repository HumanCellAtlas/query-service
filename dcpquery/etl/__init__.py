import os, re, json, tempfile, logging
from collections import OrderedDict
from contextlib import contextmanager

from dcplib.etl import DSSExtractor

from .. import config
from ..db import Bundle, File, BundleFileLink, ProcessFileLink, Process, ProcessProcessLink, DCPMetadataSchemaType

logger = logging.getLogger(__name__)


def transform_bundle(bundle_uuid, bundle_version, bundle_path, bundle_manifest_path, extractor=None):
    """
    This function is used with the ETL interface in dcplib.etl.DSSExtractor.extract.
    Given a bundle ID and directory containing its medatata JSON files, it produces an intermediate representation
    of the bundle and its files ready to be inserted into the database by BundleLoader.
    """
    result = dict(uuid=bundle_uuid,
                  version=bundle_version,
                  manifest=json.load(open(bundle_manifest_path)),
                  aggregate_metadata={},
                  files=OrderedDict())
    # Load and process all the metadata files; construct the "aggregate_metadata" doc:
    # - Singleton metadata files get inserted under their name minus the extension (project.json => {"project": {...}})
    # - Numbered metadata files are put in an array (assay_0.json, assay_1.json => {"assay": [{...0...}, {...1...}]})
    bundle_fetched_files = sorted(os.listdir(bundle_path)) if os.path.exists(bundle_path) else []
    for f in bundle_fetched_files:
        if re.match(r"(.+)_(\d+).json", f):
            metadata_key, index = re.match(r"(.+)_(\d+).json", f).groups()
        elif re.match(r"(.+).json", f):
            metadata_key, index = re.match(r"(.+).json", f).group(1), None
        else:
            metadata_key, index = f, None
        with open(os.path.join(bundle_path, f)) as fh:
            file_doc = json.load(fh)
            if index is None:
                result["aggregate_metadata"][metadata_key] = file_doc
            else:
                result["aggregate_metadata"].setdefault(metadata_key, [])
                result["aggregate_metadata"][metadata_key].append(file_doc)
        for fm in result["manifest"]["files"]:
            if f == fm["name"] and "schema_type" in file_doc:
                result["files"][fm["name"]] = dict(fm,
                                                   body=file_doc,
                                                   schema_type=file_doc['schema_type'])
    # For all other (non-metadata) files from the bundle manifest, insert them with a default body
    # indicating an empty schema type.
    for fm in result["manifest"]["files"]:
        if fm["name"] not in result["files"]:
            result["files"][fm["name"]] = dict(fm,
                                               body=None,
                                               schema_type=None)

    # Flatten the file list while preserving order.
    result["files"] = list(result["files"].values())
    return result


def get_file_extension(filename):
    try:
        regex_search_result = re.search('^(?:(?:.){1,}?)((?:[.][a-z]{1,10}){1,2})$', filename)
        file_extension = regex_search_result.group(1)
    except AttributeError:
        file_extension = None
    return file_extension


class BundleLoader:
    def __init__(self):
        schema_types = config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()
        self.schema_types = [schema[0] for schema in schema_types]

    def register_dcp_metadata_schema_type(self, schema_type):
        if schema_type and schema_type not in self.schema_types:
            schema = DCPMetadataSchemaType(name=schema_type)
            config.db_session.add(schema)
            self.schema_types.append(schema_type)

    def load_bundle(self, bundle, extractor=None, transformer=None):
        bf_links = []
        bundle_row = Bundle(uuid=bundle["uuid"],
                            version=bundle["version"],
                            manifest=bundle["manifest"],
                            aggregate_metadata=bundle["aggregate_metadata"])
        for file_data in bundle["files"]:
            filename = file_data.pop("name")
            file_extension = get_file_extension(filename)
            schema_type = None
            if file_data['body']:
                schema_type = file_data['body'].get('describedBy', '').split('/')[-1]
            if filename == "links.json":
                links = file_data['body']['links']
                load_links(links, bundle['uuid'])

            self.register_dcp_metadata_schema_type(schema_type)
            file_row = File(
                uuid=file_data['uuid'],
                version=file_data['version'],
                content_type=file_data['content-type'],
                size=file_data['size'],
                extension=str(file_extension),
                body=file_data['body'],
                dcp_schema_type_name=schema_type
            )

            bf_links.append(BundleFileLink(bundle=bundle_row, file=file_row, name=filename))
        config.db_session.add_all(bf_links)


def update_process_join_table():
    config.db_session.execute(
        """
        Insert INTO process_join_table (child_process_uuid, parent_process_uuid)
          SELECT * FROM (
              WITH
                  input_files_table AS (
                                        SELECT
                                               process_uuid AS child_process,
                                               file_uuid    AS input_file_uuid
                                        FROM process_file_join_table
                                        WHERE process_file_connection_type = 'INPUT_ENTITY'
                                      ),

                  output_files_table AS (
                                          SELECT
                                                 process_uuid AS parent_process,
                                                 file_uuid AS output_file_uuid
                                        FROM process_file_join_table
                                        WHERE process_file_connection_type = 'OUTPUT_ENTITY'
                                      )
                  SELECT
                         input_files_table.child_process,
                         output_files_table.parent_process
                  FROM input_files_table, output_files_table
       WHERE input_files_table.input_file_uuid = output_files_table.output_file_uuid) AS temp_tables
       ON CONFLICT DO NOTHING;
        """
    )
    config.db_session.commit()


def commit_to_db(extracted_bundles):
    config.db_session.commit()


def dcpquery_etl_finalizer(extractor):
    create_materialized_view_tables()
    update_process_join_table()


def update_bundles_materialized_view():
    config.db_session.execute(
        """
        REFRESH MATERIALIZED VIEW CONCURRENTLY bundles
        """
    )


def update_files_materialized_view():
    config.db_session.execute(
        """
        REFRESH MATERIALIZED VIEW CONCURRENTLY files
        """
    )


def create_dcp_schema_type_materialized_views(matviews):
    schema_types = [schema[0] for schema in
                    config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()]
    for schema_type in schema_types:
        if schema_type not in matviews:
            config.db_session.execute(
                f"""
                  CREATE MATERIALIZED VIEW {schema_type} AS
                  SELECT f.* FROM files as f
                  WHERE f.dcp_schema_type_name = '{schema_type}'
                """
            )
            config.db_session.execute(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {schema_type+'_idx'} ON {schema_type} (fqid);

                """
            )
        else:
            config.db_session.execute(
                f"""
                REFRESH MATERIALIZED VIEW CONCURRENTLY {schema_type}
                """
            )


def create_materialized_view_tables():
    matviews = [x[0] for x in config.db_session.execute("SELECT matviewname FROM pg_catalog.pg_matviews;").fetchall()]
    config.reset_db_timeout_seconds(880)
    update_bundles_materialized_view()
    update_files_materialized_view()
    create_dcp_schema_type_materialized_views(matviews)
    config.db_session.commit()


def load_links(links, bundle_uuid):
    for link in links:
        try:
            process = format_process_info(link)
            config.db_session.add(Process(process_uuid=process['process_uuid']))
            create_process_file_links(process)
        except AssertionError as e:
            logger.error(f"Error while loading link for bundle: {bundle_uuid} error: {e}")


def format_process_info(link):
    assert 'process' in link
    process_uuid = link['process']
    protocol_uuids = []
    for protocol in link['protocols']:
        protocol_uuid = protocol['protocol_id']
        protocol_uuids.append(protocol_uuid)

    return {"process_uuid": process_uuid, "input_file_uuids": link["inputs"], "output_file_uuids": link["outputs"],
            "protocol_uuids": protocol_uuids}


def create_process_file_links(process):
    process_file_links = []
    input_file_uuids = process['input_file_uuids']
    output_file_uuids = process['output_file_uuids']
    protocol_uuids = process['protocol_uuids']

    for file_uuid in input_file_uuids:
        process_file_links.append(
            ProcessFileLink(
                process_uuid=process['process_uuid'],
                file_uuid=file_uuid,
                process_file_connection_type='INPUT_ENTITY'
            )
        )

    for file_uuid in output_file_uuids:
        process_file_links.append(
            ProcessFileLink(
                process_uuid=process['process_uuid'],
                file_uuid=file_uuid,
                process_file_connection_type='OUTPUT_ENTITY'
            )
        )

    for file_uuid in protocol_uuids:
        process_file_links.append(
            ProcessFileLink(
                process_uuid=process['process_uuid'],
                file_uuid=file_uuid,
                process_file_connection_type='PROTOCOL_ENTITY'
            )
        )

    config.db_session.add_all(process_file_links)


def etl_one_bundle(bundle_uuid, bundle_version):
    extractor = DSSExtractor(staging_directory=tempfile.gettempdir(), dss_client=config.dss_client)
    os.makedirs(f"{extractor.sd}/files", exist_ok=True)
    os.makedirs(f"{extractor.sd}/bundles", exist_ok=True)
    _, _, files_to_fetch = extractor.get_files_to_fetch_for_bundle(bundle_uuid, bundle_version)
    for f in files_to_fetch:
        extractor.get_file(f, bundle_uuid, bundle_version)

    bundle_path = f"{extractor.sd}/bundles/{bundle_uuid}.{bundle_version}"
    bundle_manifest_path = f"{extractor.sd}/bundle_manifests/{bundle_uuid}.{bundle_version}.json"
    tb = transform_bundle(bundle_uuid=bundle_uuid, bundle_version=bundle_version, bundle_path=bundle_path,
                          bundle_manifest_path=bundle_manifest_path, extractor=extractor)
    BundleLoader().load_bundle(extractor=extractor, transformer=transform_bundle, bundle=tb)


def drop_one_bundle(bundle_uuid, bundle_version):
    bundle_fqid = bundle_uuid + '.' + bundle_version
    file_fqids = [link[1] for link in BundleFileLink.select_links_for_bundle_fqids([bundle_fqid])]
    BundleFileLink.delete_links_for_bundles([bundle_fqid])
    files_to_keep = [link[1] for link in BundleFileLink.select_links_for_file_fqids(file_fqids)]
    files_to_delete = list(set(file_fqids) - set(files_to_keep))
    # TODO @madison once processes link to file versions cascade file deletions to associated processes
    File.delete_files(files_to_delete)
    Bundle.delete_bundles([bundle_fqid])
    config.db_session.commit()


def process_bundle_event(dss_event):
    config.readonly_db = False
    config.reset_db_session()
    if dss_event["event_type"] == "CREATE":
        etl_one_bundle(**dss_event["match"])
    elif dss_event["event_type"] in {"TOMBSTONE", "DELETE"}:
        drop_one_bundle(**dss_event["match"])
    else:
        logger.error("Ignoring unknown event type %s", dss_event["event_type"])
