import os, tempfile, logging

from dcplib.etl import DSSExtractor

from dcpquery.etl.load import BundleLoader
from dcpquery.etl.transform import transform_bundle

from .. import config
from ..db import Bundle, File, BundleFileLink, DCPMetadataSchemaType

logger = logging.getLogger(__name__)


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
