import os, tempfile, logging

from dcplib.etl import DSSExtractor

from dcpquery.db.materialized_views import create_materialized_view_tables
from dcpquery.etl.extract import extract_bundles, divide_chunks
from dcpquery.etl.old_load import load_bundle
from dcpquery.etl.output import bundle_uuids
from dcpquery.etl.transform import transform_bundle

from .. import config

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


def etl_bundles():
    n = 100
    counter = 0
    x = list(divide_chunks(bundle_uuids, n))
    for i in x:
        print(counter)
        bundles = extract_bundles(i)
        for bundle in bundles['results']:
            load_bundle(bundle=bundle)
        counter += 1
    config.db_session.commit()
