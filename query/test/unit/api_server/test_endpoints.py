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

    @patch('query.lambdas.api_server.v1.endpoints.db.run_read_only_query')
    def test_query_endpoint(self, mock_ro_query):
        column_names = ['uuid', 'version', 'fqid', 'name', 'schema_type_id', 'json']
        mock_ro_query.return_value = fast_query_mock_result, column_names
        self.client = client_for_test_api_server()
        query = "Select * From files;"
        response = self.client.post(f"/v1/query", data=json.dumps(query))
        self.assertEqual(response.status_code, 200)
        expected_response_data = {"query": query, "results": fast_query_expected_results}
        self.assertEqual(json.loads(response.data), expected_response_data)

    @patch('query.lambdas.api_server.v1.endpoints.sqs_client')
    def test_webhook_endpoint(self, mock_sqs_client):
        mock_sqs_client.send_message.return_value = {}
        subscription_data = {
            "transaction_id": "ad36ec67-32a6-4886-93a9-29caf11e8ea8",
            "subscription_id": "3caf5b8e-2c03-4905-9785-d2b02df4ecbd",
            "es_query": {
                "query": {
                    "match_all": {}
                }
            },
            "match": {
                "bundle_uuid": "72f39c2d-d5cb-440d-8964-33169faf6b11",
                "bundle_version": "2018-12-03T162944.061337Z"
            }
        }
        self.client = client_for_test_api_server()

        response = self.client.post("v1/webhook", data=json.dumps(subscription_data))
        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/861229788715/dcp-query-data-input-queue-dev',
            MessageBody=json.dumps(subscription_data['match'])
        )

        self.assertEqual(response.status_code, 202)