import os
import sys
import unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from query.test.unit.api_server import client_for_test_api_server


class TestHealthCheckEndpoint(unittest.TestCase):

    def test_heathcheck_endpoint(self):
        self.client = client_for_test_api_server()

        response = self.client.get(f"/v1/health")

        self.assertEqual(response.status_code, 200)

