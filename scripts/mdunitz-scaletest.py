import concurrent.futures
import gzip
import json
import time
import unittest
import brotli
import requests
from chalice.local import LocalGatewayException, LocalGateway
from dcplib.networking import HTTPRequest

async_queries = {}
quick_queries = {
    "get_files": "SELECT * FROM files limit 10;",
    "get_bundles": "SELECT * FROM bundles limit 10;",
    "get_processes_for_graph": "SELECT * FROM processes_for_graph limit 10;",
    "bundle_count": "SELECT COUNT(*) from bundles;",
    "all_bundles_count": "SELECT COUNT(*) from bundles_all_versions;",
    "files_count": "SELECT COUNT(*) from files;",
    "all_files_count": "SELECT COUNT(*) from files_all_versions"
}
quick_queries_list = ["SELECT * FROM files limit 10;",
                      "SELECT * FROM bundles limit 10;",
                      "SELECT * FROM processes_for_graph limit 10;",
                      "SELECT COUNT(*) from bundles;",
                      "SELECT COUNT(*) from bundles_all_versions;",
                      "SELECT COUNT(*) from files;",
                      "SELECT COUNT(*) from files_all_versions"
                      ]


class TestRequestScale(unittest.TestCase):
    url = "https://query.integration.data.humancellatlas.org/v1/query"

    # gateway = LocalGateway(self._chalice_app, config)
    @classmethod
    def setUpClass(cls):
        cls.start = time.time()
        cls.scale = 64

    @classmethod
    def tearDownClass(cls):
        cls.end = time.time()
        print(f"Total time {round(cls.end - cls.start)} seconds")

    def _make_query(self, query):
        query_start = time.time()
        data = json.dumps({'query': query})
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, data=data)
        print(f"QUERY: {query} ran in {time.time()-query_start} seconds")
        print(response.content)
        return response, query, time.time() - query_start

    def test_queries_run_sequentially(self):
        self.sequential_start = time.time()
        i = 0
        while i < self.scale:
            query = quick_queries_list[i % len(quick_queries_list)]
            result, query, t = self._make_query(query)
            try:
                assert result.status_code in (200, 301)
                if result.status_code == 301:
                    print(f'301: {query}')
                print(f'OK: {query}')
            except Exception as e:
                print(f"FAILURE FAILURE FAILURE FAILURE FAILURE THIS SHOULD BE EASY TO SPOT, {e}")
            i += 1
        self.sequential_end = time.time()
        print(
            f"Processed {self.scale} requests sequentially in {round(self.sequential_end - self.sequential_start)} seconds")

    def test_queries_run_in_parallel(self):
        self.parallel_start = time.time()
        problems = []
        query_times = {"SELECT * FROM files limit 10;": [],
                       "SELECT * FROM bundles limit 10;": [],
                       "SELECT * FROM processes_for_graph limit 10;": [],
                       "SELECT COUNT(*) from bundles;": [],
                       "SELECT COUNT(*) from bundles_all_versions;": [],
                       "SELECT COUNT(*) from files;": [],
                       "SELECT COUNT(*) from files_all_versions": []}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            i = 0
            while i < self.scale:
                if i % 100 == 0:
                    print(
                        f"**************************************************************************{i} requests made")
                query = quick_queries_list[i % len(quick_queries_list)]
                f = executor.submit(self._make_query, query)
                futures.append(f)
                i += 1
            for future in concurrent.futures.as_completed(futures):
                try:
                    result, query, seconds = future.result()
                    query_times[query].append(seconds)
                    assert result.status_code in (200, 301)
                    if result.status_code == 301:
                        print(f'returned a 301: {query}')
                except Exception as e:
                    problems.append({'error': e, 'status_code': result.status_code, 'result': result, 'query': query})
        self.parallel_end = time.time()
#        try:
#            assert len(problems) == 0
#        except:
#            import pdb
#            pdb.set_trace()
        print(f"Processed {self.scale} requests parallel in {round(self.parallel_end - self.parallel_start)} seconds")

if __name__ == "__main__":
    unittest.main()
