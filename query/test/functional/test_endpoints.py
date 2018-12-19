import json
import os
import unittest

import requests

from lib.config import Config


class TestQueryService(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deployment_stage = Config.deployment_stage
        self.api_url = Config.api_url
        print(f"\n\nTESTING ENVIRONMENT {self.deployment_stage} at URL {self.api_url}. \n")

    def test_health_check(self):
        response = self._make_request(
            description='CHECK SERVICE HEALTH',
            verb='GET',
            url=f"{self.api_url}/health",
            expected_status=200)
        print(f"RESPONSE: {response}")

    def test_query(self):
        query = "SELECT count(*) FROM FILES;"
        response = self._make_request(
            description='CHECK QUERY ENDPOINT',
            verb='POST',
            url=f"{self.api_url}/query",
            data=json.dumps(query),
            expected_status=200
        )
        self.assertEqual(json.loads(response)['query'], query)
        self.assertGreaterEqual(json.loads(response)['results'][0]['count'], 0)

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
