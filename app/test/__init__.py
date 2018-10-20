import functools
import os
import json
import random
import string
import sys
import time
import typing

from psycopg2 import sql

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from lib.extract import Extractor
from lib.model import Bundle, BundleManifest, File, FileMetadata
from lib.logger import logger


def load_fixture(fixture_file):
    with open('test/fixtures/' + fixture_file, 'r') as fh:
        txt = fh.read()
    return txt


vx_bundle_fqid = '0c8d7f15-47c2-42c2-83de-47ae48e1eae1.2018-09-06T190237.485774Z'
vx_bundle_str = load_fixture('vx_bundle.json')

vx_bundle = Bundle(
    fqid=vx_bundle_fqid,
    bundle_manifest=BundleManifest(**json.loads(vx_bundle_str)),
    files=[
        File(
            FileMetadata(d),
            **json.loads(load_fixture(d['name']))
        )
        for d in json.loads(vx_bundle_str)['files'] if d['name'].endswith('.json')
    ]
)


class FixtureExtractor(Extractor):

    _key_to_fixture_map = dict([
        (d.uuid, load_fixture(d.name))
        for d in BundleManifest(**json.loads(vx_bundle_str)).file_metadata
    ])
    _key_to_fixture_map[vx_bundle.uuid] = vx_bundle_str

    def _extract(self, key: str):
        data = self._key_to_fixture_map[key]
        return self._deserialize(data)

    def extract_bundle(self, key: str, version: typing.Optional[str]=None):
        return self._extract(key)

    def extract_file(self, key: str, version: typing.Optional[str]=None):
        return self._extract(key)


def gen_random_chars(n: int):
    return ''.join(
        [random.choice(string.ascii_lowercase)] +
        [random.choice(string.ascii_lowercase + string.digits) for _ in range(n-1)]
    )


def eventually(timeout: float, interval: float, errors: set={AssertionError}):
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
    cursor.execute("TRUNCATE TABLE metadata_modules CASCADE")
    cursor.execute("TRUNCATE TABLE metadata_files CASCADE")
    cursor.execute("TRUNCATE TABLE bundles CASCADE")
