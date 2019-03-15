import json
import os
import unittest

import requests

from dcpquery import config


@unittest.skip("WIP")
class TestQueryService(unittest.TestCase):

    def setUp(self):

        _api_host = os.getenv("API_HOST")
        self.api_url = f"https://{_api_host}/v1"
        print(f"\n\nTESTING ENVIRONMENT {config.stage} at URL {self.api_url}. \n")

    def test_health_check(self):
        self._make_request(
            description='CHECK SERVICE HEALTH',
            verb='GET',
            url=f"{self.api_url}/health",
            expected_status=200)

    def test_query(self):
        query = "SELECT count(*) FROM FILES;"
        self.request = self._make_request(description='CHECK QUERY ENDPOINT', verb='POST',
                                          url=f"{self.api_url}/query", data=json.dumps(query), expected_status=200)
        response = self.request
        self.assertEqual(json.loads(response)['query'], query)
        self.assertGreaterEqual(json.loads(response)['results'][0]['count'], 0)

    def test_create_async_query(self):
        query = "SELECT * FROM FILES LIMIT 1;"
        response = self._make_request(
            description='CHECK CREATE LONG QUERIES ENDPOINT',
            verb='POST',
            url=f"{self.api_url}/query/async",
            data=json.dumps(query),
            expected_status=202
        )
        self.assertEqual(json.loads(response)['query'], query)
        self.assertTrue(json.loads(response)['job_id'])

    def test_get_job_status(self):
        # create job
        query = "SELECT * FROM FILES LIMIT 1;"
        response = self._make_request(
            description='CHECK CREATE LONG QUERIES ENDPOINT',
            verb='POST',
            url=f"{self.api_url}/query/async",
            data=json.dumps(query),
            expected_status=202
        )
        job_id = json.loads(response)['job_id']
        response = self._make_request(
            description='CHECK GET LONG QUERIES ENDPOINT',
            verb='GET',
            url=f"{self.api_url}/query/async/{job_id}",
            expected_status=200
        )
        self.assertEqual(json.loads(response)['job_id'], job_id)
        self.assertIn(json.loads(response)['status'], ['CREATED', 'PROCESSING', 'COMPLETE', 'FAILED'])
        # TODO check if complete it returns a s3_url

    def test_get_job_status_for_uncreated_job(self):
        job_id = '713bf52c-daa4-4ac7-8508-466add356e88'
        self._make_request(
            description='CHECK GET LONG QUERIES ENDPOINT',
            verb='GET',
            url=f"{self.api_url}/query/async/{job_id}",
            expected_status=404
        )

    def _make_request(self, description, verb, url, expected_status=None, **options):
        print(description + ": ")
        print(f"{verb.upper()} {url}")

        method = getattr(requests, verb.lower())
        response = method(url, **options)

        print(f"-> {response.status_code}")
        if expected_status:
            self.assertEqual(expected_status, response.status_code)

        if response.content:
            print(response.content.decode('utf8'))

        return response.content
