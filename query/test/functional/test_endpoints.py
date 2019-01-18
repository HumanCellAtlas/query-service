import json
import unittest

import requests

from lib.config import Config


class TestQueryService(unittest.TestCase):

    def setUp(self):
        print(f"\n\nTESTING ENVIRONMENT {Config.deployment_stage} at URL {Config.api_url}. \n")

    def test_health_check(self):
        self._make_request(
            description='CHECK SERVICE HEALTH',
            verb='GET',
            url=f"{Config.api_url}/health",
            expected_status=200)

    def test_query(self):
        query = "SELECT count(*) FROM FILES;"
        response = self._make_request(
            description='CHECK QUERY ENDPOINT',
            verb='POST',
            url=f"{Config.api_url}/query",
            data=json.dumps(query),
            expected_status=200
        )
        self.assertEqual(json.loads(response)['query'], query)
        self.assertGreaterEqual(json.loads(response)['results'][0]['count'], 0)

    def test_create_long_running_query(self):
        query = "SELECT * FROM FILES LIMIT 1;"
        response = self._make_request(
            description='CHECK CREATE LONG QUERIES ENDPOINT',
            verb='POST',
            url=f"{Config.api_url}/long-running-query",
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
            url=f"{Config.api_url}/long-running-query",
            data=json.dumps(query),
            expected_status=202
        )
        job_id = json.loads(response)['job_id']
        response = self._make_request(
            description='CHECK GET LONG QUERIES ENDPOINT',
            verb='GET',
            url=f"{Config.api_url}/long-running-query/{job_id}",
            expected_status=200
        )
        self.assertEqual(json.loads(response)['job_id'], job_id)
        self.assertIn(json.loads(response)['status'], ['CREATED', 'PROCESSING', 'COMPLETE', 'FAILED'])
        # TODO check if complete it returns a s3_url

    def test_get_job_status__for_uncreated_job(self):
        job_id = '713bf52c-daa4-4ac7-8508-466add356e88'
        self._make_request(
            description='CHECK GET LONG QUERIES ENDPOINT',
            verb='GET',
            url=f"{Config.api_url}/long-running-query/{job_id}",
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


