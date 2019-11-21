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
        logger.warning("CHECK CREATE ASYNC QUERIES ENDPOINT")
        query = "SELECT * FROM FILES LIMIT 1;"
        response = self.assertPostResponse(f"{self.api_url}/v1/query_job",
                                           json_request_body=dict(query=query),
                                           expected_code=requests.codes.accepted)
        self.assertEqual(response.json['query'], query)
        self.assertRegex(response.json['job_id'], ".{8}-.{4}-.{4}-.{4}-.{12}")

    def test_get_job_status(self):
        logger.warning("CHECK ASYNC QUERY STATUS ENDPOINT")
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

    def test_get_bundle_fqids_for_file_endpoint(self):
        logger.warning("Check files/{file_uuid}/bundles endpoint")
        file_uuid = str(config.db_session.execute("SELECT uuid from files limit 1").fetchall()[0][0])


        response = self.assertGetResponse(
            f"{self.api_url}/v1/files/{file_uuid}/bundles",
            params=dict(check_events=False),
            expected_code=requests.codes.ok
        )
        self.assertGreater(len(response.json['bundle_fqids']), 0)


    def test_get_file_fqids_for_schema_type_endpoint(self):
        logger.warning("Check files/schema/{schema_type} endpoint")
        schema_information = config.db_session.execute(
            "SELECT dcp_schema_type_name, schema_major_version, schema_minor_version FROM files LIMIT 1;"
        ).fetchall()[0]
        schema_type = schema_information[0]
        major = schema_information[1]
        minor = schema_information[2]

        response = self.assertGetResponse(
            f"{self.api_url}/v1/files/schema/{schema_type}",
            params=dict(version=str(major) + '.' + str(minor)),
            expected_code=requests.codes.ok
        )
        self.assertGreater(len(response.json['file_fqids']), 0)


if __name__ == '__main__':
    unittest.main()
