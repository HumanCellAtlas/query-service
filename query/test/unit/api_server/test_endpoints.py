import unittest

from unittest.mock import patch
from test import *

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from query.test.unit.api_server import client_for_test_api_server


class TestEndpoints(unittest.TestCase):

    def test_heathcheck_endpoint(self):
        self.client = client_for_test_api_server()

        response = self.client.get(f"/v1/health")

        self.assertEqual(response.status_code, 200)

    @patch('query.lambdas.api_server.v1.fast_query.db.run_read_only_query')
    def test_query_endpoint(self, mock_ro_query):
        self.maxDiff = None

        column_names = ['uuid', 'version', 'fqid', 'name', 'schema_type_id', 'json']
        mock_ro_query.return_value = fast_query_mock_result['mock_result'], column_names
        self.client = client_for_test_api_server()
        query = "Select * From files;"
        response = self.client.post(f"/v1/query", data=json.dumps(query))
        self.assertEqual(response.status_code, 200)
        expected_response_data = {"query": query, "results": fast_query_expected_results['expected_result']}
        self.assertEqual(json.loads(response.data), expected_response_data)
