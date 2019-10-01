import concurrent.futures
import json
import os
import time
import unittest
import requests

from dcpquery.utils import get_secret, post_to_slack
from tests import logger


class TestRequestScale(unittest.TestCase):
    def __init__(self, threads, scale, stage):
        self.threads = threads
        self.scale = scale
        if stage == 'prod':
            self.url = "https://query.data.humancellatlas.org/v1/query"
        else:
            self.url = f"https://query.{stage}.data.humancellatlas.org/v1/query"
        self.quick_queries_list = ["SELECT * FROM files limit 10;",
                                   "SELECT * FROM bundles limit 10;",
                                   "SELECT * FROM processes_for_graph limit 10;",
                                   "SELECT COUNT(*) from bundles;",
                                   "SELECT COUNT(*) from bundles_all_versions;",
                                   "SELECT COUNT(*) from files;",
                                   "SELECT COUNT(*) from files_all_versions"
                                   ]
        self.async_queries_list = [
            """
            SELECT pg_sleep(35);
            SELECT DISTINCT (body->'project_core'->>'project_title') AS title
              FROM files WHERE dcp_schema_type_name = 'project';
            """,
            """
            SELECT pg_sleep(35);
            SELECT count(distinct (bfl_id.bundle_fqid))
            FROM (SELECT * FROM (
            SELECT fqid, body->'library_construction_approach'->>'text' AS library FROM library_preparation_protocol
            ) AS t
            JOIN bundle_file_links AS bfl
            ON bfl.file_fqid = t.fqid
            WHERE t.library = 'Smart-seq2') AS bfl_id;
            """,
            """
            SELECT pg_sleep(35);
            SELECT * FROM (WITH method_table AS (
            SELECT fqid, body->'method'->>'text' AS method
            from dissociation_protocol
            ) SELECT method, COUNT(method) FROM method_table
            GROUP BY method) AS foo;
            """
        ]

    def _make_query(self, query):
        query_start = time.time()
        data = json.dumps({'query': query})
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, data=data, allow_redirects=False)
        query_run_time = round(time.time() - query_start)
        logger.debug(f"Query: {query} ran in {query_run_time} seconds")
        return response, query_run_time

    def _get_file_uuids(self):
        response, _ = self._make_query(f"SELECT uuid FROM files limit {self.scale};")
        uuid_list = [x['uuid'] for x in json.loads(response._content)['results']]
        return uuid_list

    def _create_graph_traversal_query(self, file_uuid):
        return f"""
                select * from (
                  select file_uuid
                  from process_file_join_table
                  where process_uuid in (
                      select get_all_children(process_uuid)
                      from process_file_join_table
                      where file_uuid = '{file_uuid}'
                  )
                ) as child_table
                join files on child_table.file_uuid = files.uuid
                UNION
                select * from (
                  select file_uuid from process_file_join_table
                  where process_uuid in (
                    select get_all_parents(process_uuid) from process_file_join_table
                    where file_uuid = '{file_uuid}'
                  )
                ) as parent_table
               join files on parent_table.file_uuid = files.uuid;
               """

    # Not currently run, useful for comparing to and debugging issues with parallel tests
    def test_basic_queries_run_sequentially(self):
        start = time.time()
        i = 0
        while i < self.scale:
            query = self.quick_queries_list[i % len(self.quick_queries_list)]
            try:
                result, seconds = self._make_query(query)
                assert result.status_code in (200, 302)
                if result.status_code == 301:
                    print(f'returned a 301: {query}')
            except Exception as e:
                print(f"Issue with the query, {e}")
            i += 1
        end = time.time()
        sequential_run_time = round(end - start)
        print(f"{self.scale} queries ran sequentially in: {sequential_run_time} seconds")

    def test_basic_queries_run_in_parallel(self):
        start = time.time()
        problems = []
        redirects = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            i = 0
            while i < self.scale:
                query = self.quick_queries_list[i % len(self.quick_queries_list)]
                f = executor.submit(self._make_query, query)
                futures[f] = query
                i += 1
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = None
                    result, seconds = future.result()
                    query = futures[future]
                    assert result.status_code in (200, 302)
                    if result.status_code == 302:
                        redirects.append(result)
                except Exception as e:
                    problems.append({'error': e, 'status_code': result.status_code, 'result': result, 'query': query})
        end = time.time()
        basic_query_time = round(end - start)
        basic_query_redirects = len(redirects)
        basic_query_problems = len(problems)
        return basic_query_time, basic_query_problems, basic_query_redirects

    def test_async_queries_run_in_parallel(self):
        start = time.time()
        problems = []
        redirects = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            i = 0
            while i < self.scale:
                query = self.async_queries_list[i % len(self.async_queries_list)]
                f = executor.submit(self._make_query, query)
                futures[f] = query
                i += 1
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = None
                    result, seconds = future.result()
                    query = futures[future]
                    assert result.status_code in (200, 302)
                    if result.status_code == 302:
                        redirects.append(result)
                except Exception as e:
                    problems.append({'error': e, 'status_code': result.status_code, 'result': result, 'query': query})
        end = time.time()
        async_query_time = round(end - start)
        async_query_redirects = len(redirects)
        async_query_problems = len(problems)
        return async_query_time, async_query_problems, async_query_redirects

    def test_graph_traversal_queries_run_in_parallel(self):
        start = time.time()
        problems = []
        redirects = []
        file_uuids = self._get_file_uuids()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            for file_uuid in file_uuids:
                query = self._create_graph_traversal_query(file_uuid)

                f = executor.submit(self._make_query, query)
                futures[f] = query
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = None
                    result, seconds = future.result()
                    query = futures[future]
                    assert result.status_code in (200, 302)
                    if result.status_code == 302:
                        redirects.append(result)
                except Exception as e:
                    problems.append({'error': e, 'status_code': result.status_code, 'result': result, 'query': query})
        end = time.time()
        graph_traversal_time = round(end - start)
        graph_traversal_redirects = len(redirects)
        graph_traversal_problems = len(problems)
        return graph_traversal_time, graph_traversal_problems, graph_traversal_redirects


if __name__ == '__main__':
    stage = os.getenv('STAGE')
    scale = 500
    threads = 50
    scale_test = TestRequestScale(scale=scale, threads=threads, stage=stage)
    start = time.time()
    print("Starting test_basic_queries_run_in_parallel")
    basic_query_time, basic_query_problems, basic_query_redirects = scale_test.test_basic_queries_run_in_parallel()
    print("Starting test_async_queries_run_in_parallel")
    async_query_time, async_query_problems, async_query_redirects = scale_test.test_async_queries_run_in_parallel()
    print("Starting test_graph_traversal_queries_run_in_parallel")
    gt_time, gt_problems, gt_redirects = scale_test.test_graph_traversal_queries_run_in_parallel()
    end = time.time()
    message = f"""
    Scale test in {stage} environment ran {scale} queries per test with {threads} threads in {round(end-start)} seconds.
    Basic queries: {basic_query_time} second(s), {basic_query_problems} problem(s), {basic_query_redirects} redirect(s)
    Async queries: {async_query_time} second(s), {async_query_problems} problem(s), {async_query_redirects} redirect(s)
    Graph traversal queries: {gt_time} second(s), {gt_problems} problem(s), {gt_redirects} redirect(s)
    """
    print(message)
    slack_url = json.loads(get_secret("dcp/query/slackalert"))['SLACK_WEBHOOK']
    post_to_slack(message, slack_url)
