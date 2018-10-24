import os
import sys

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from query.test.unit import QueryTestCaseUsingMockAWS
from query.test.unit.api_server import client_for_test_api_server


class TestHealthCheckEndpoint(QueryTestCaseUsingMockAWS):

    def test_heathcheck_endpoint(self):
        import pdb
        # pdb.set_trace()
        self.client = client_for_test_api_server()

        response = self.client.get(f"/v1/health")

        self.assertEqual(response.status_code, 200)

