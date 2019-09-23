import os, json, unittest, logging

import requests

from dcplib.networking import http
from dcplib.test_helpers import DCPAssertMixin

from dcpquery import config

from tests import eventually

logger = logging.getLogger(__name__)


class TestQueryService(unittest.TestCase, DCPAssertMixin):
    def setUp(self):
        self.api_url = f"https://{os.environ['API_DOMAIN_NAME']}"
        self.app = http
        logger.warning(f"\n\nTESTING ENVIRONMENT {config.stage} at URL {self.api_url}. \n")

    def test_health_check(self):
        logger.warning("CHECK SERVICE HEALTH")
        self.assertGetResponse(f"{self.api_url}/internal/health", expected_code=requests.codes.ok)

    def test_query(self):
        logger.warning("CHECK QUERY ENDPOINT")
        query = "SELECT count(*) FROM FILES;"
        response = self.assertPostResponse(f"{self.api_url}/v1/query",
                                           json_request_body=dict(query=query),
                                           expected_code=requests.codes.ok)
        self.assertEqual(response.json['query'], query)
        self.assertGreaterEqual(response.json['results'][0]['count'], 0)

        query = "SELECT count(*) FROM FILES WHERE SIZE > %(s)s;"
        params = {"s": 0}
        response = self.assertPostResponse(f"{self.api_url}/v1/query",
                                           json_request_body=dict(query=query, params=params),
                                           expected_code=requests.codes.ok)
        self.assertEqual(response.json['query'], query)
        self.assertGreaterEqual(response.json['results'][0]['count'], 0)

    def test_create_async_query(self):
        logger.warning("CHECK CREATE LONG QUERIES ENDPOINT")
        query = "SELECT * FROM FILES LIMIT 1;"
        response = self.assertPostResponse(f"{self.api_url}/v1/query_job",
                                           json_request_body=dict(query=query),
                                           expected_code=requests.codes.accepted)
        self.assertEqual(response.json['query'], query)
        self.assertRegex(response.json['job_id'], ".{8}-.{4}-.{4}-.{4}-.{12}")

    def test_get_job_status(self):
        logger.warning("CHECK GET LONG QUERIES ENDPOINT")
        query = "SELECT * FROM FILES LIMIT 1;"
        response = self.assertPostResponse(f"{self.api_url}/v1/query_job",
                                           json_request_body=dict(query=query),
                                           expected_code=requests.codes.accepted)
        job_id = response.json["job_id"]
        response = self.assertGetResponse(f"{self.api_url}/v1/query_jobs/{job_id}", expected_code=requests.codes.ok)
        self.assertEqual(response.json['job_id'], job_id)
        self.assertIn(response.json['status'], ['new', 'running', 'done'])

        @eventually(10, 1)
        def get_job_result(job_id):
            return self.assertGetResponse(f"{self.api_url}/v1/query_jobs/{job_id}",
                                          params=dict(redirect_when_waiting=True, redirect_when_done=True),
                                          expected_code=requests.codes.ok)

        response = get_job_result(job_id)
        self.assertEqual(response.response.headers["Server"], "AmazonS3")
        self.assertEqual(response.json["job_id"], job_id)
        self.assertEqual(response.json["status"], "done")
        self.assertEqual(response.json["error"], None)
        self.assertIsInstance(response.json["result"], list)
        self.assertGreaterEqual(len(response.json["result"]), 0)

    def test_get_job_status_for_uncreated_job(self):
        logger.warning("CHECK GET LONG QUERIES ENDPOINT (UNKNOWN JOB)")
        job_id = '713bf52c-daa4-4ac7-8508-466add356e88'
        self.assertGetResponse(f"{self.api_url}/v1/query_jobs/{job_id}", expected_code=requests.codes.not_found)

    def test_cors(self):
        FIXME


if __name__ == '__main__':
    unittest.main()
