import functools
import os
import json
import random
import string
import sys
import time
import logging
from uuid import UUID

from psycopg2 import sql

from dcplib.etl import DSSExtractor
from dcpquery.db import Bundle, File, BundleFileLink
from dcpquery import config

config.configure_logging()
logger = logging.getLogger(__name__)


def load_fixture(fixture_file):
    with open(f'{os.path.dirname(__file__)}/fixtures/{fixture_file}', 'r') as fh:
        txt = fh.read()
    return txt


vx_bundle_uuid = '0c8d7f15-47c2-42c2-83de-47ae48e1eae1'
vx_bundle_version = '2018-09-06T190237.485774Z'
vx_bundle_fqid = f'{vx_bundle_uuid}.{vx_bundle_version}'
vx_bundle_manifest = load_fixture('vx_bundle.json')
vx_bundle_aggregate_md = json.loads(load_fixture('vx_bundle_document.json'))
fast_query_mock_result = json.loads(load_fixture('fast_query_mock_result.json'))
fast_query_expected_results = json.loads(load_fixture('fast_query_expected_results.json'))
mock_links = json.loads(load_fixture('process_links.json'))
vx_bundle = Bundle(fqid=vx_bundle_fqid,
                   manifest=json.loads(vx_bundle_manifest),
                   aggregate_metadata=vx_bundle_aggregate_md)
vx_bf_links = []

for f in json.loads(vx_bundle_manifest)['files']:
    if f["content-type"] == "application/json":
        f_row = File(uuid=f["uuid"], version=f["version"], body=json.loads(load_fixture(f["name"])),
                     content_type=f["content-type"], size=f["size"])
        vx_bf_links.append(BundleFileLink(bundle=vx_bundle, file=f_row, name=f["name"]))


def write_fixtures_to_db():
    config.db_session.add_all(vx_bf_links)
    config.db_session.commit()


def eventually(timeout: float, interval: float, errors: set = {AssertionError}):
    """
    @eventually runs a test until all assertions are satisfied or a timeout is reached.
    :param timeout: time until the test fails
    :param interval: time between attempts of the test
    :param errors: the exceptions to catch and retry on
    :return: the result of the function or a raised assertion error
    """

    def decorate(func):
        @functools.wraps(func)
        def call(*args, **kwargs):
            timeout_time = time.time() + timeout
            error_tuple = tuple(errors)
            while True:
                try:
                    return func(*args, **kwargs)
                except error_tuple as e:
                    if time.time() >= timeout_time:
                        raise
                    logger.debug("Error in %s: %s. Retrying after %s s...", func, e, interval)
                    time.sleep(interval)
                    ''

        return call

    return decorate


def clear_views(cursor):
    cursor.execute(
        """
        SELECT table_name
            FROM information_schema.views
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            AND table_name !~ '^pg_';
        """
    )
    views = [ele[0] for ele in cursor.fetchall()]
    for view in views:
        cursor.execute(
            sql.SQL(
                f"DROP VIEW {view};"
            )
        )


def truncate_tables(cursor):
    cursor.execute("TRUNCATE TABLE files CASCADE")
    cursor.execute("TRUNCATE TABLE bundles CASCADE")
    cursor.execute("TRUNCATE TABLE bundles_files CASCADE")
    cursor.execute("TRUNCATE TABLE job_status CASCADE")
    cursor.execute("TRUNCATE TABLE process_links_join_table CASCADE")
    cursor.execute("TRUNCATE TABLE hca_processes CASCADE")
