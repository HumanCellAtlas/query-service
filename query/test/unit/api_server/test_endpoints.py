import json
import unittest

from unittest.mock import patch

from lib.config import Config
from test import fast_query_mock_result, fast_query_expected_results
from test.unit.api_server import client_for_test_api_server


class TestEndpoints(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = client_for_test_api_server()
        self.uuid = "3d8608c3-0ca6-430a-9f90-2117be6af160"

    def test_healthcheck_endpoint(self):
        response = self.client.get(f"/v1/health")
        self.assertEqual(response.status_code, 200)

    @patch('query.lambdas.api_server.v1.endpoints.db.run_read_only_query')
    def test_query_endpoint(self, mock_ro_query):
        column_names = ['uuid', 'version', 'fqid', 'name', 'schema_type_id', 'json']
        mock_ro_query.return_value = fast_query_mock_result, column_names
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
        response = self.client.post("v1/webhook", data=json.dumps(subscription_data))
        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=Config.load_data_queue_url,
            MessageBody=json.dumps(subscription_data['match'])
        )

        self.assertEqual(response.status_code, 202)

    @patch('query.lambdas.api_server.v1.endpoints.sqs_client')
    @patch('query.lambdas.api_server.v1.endpoints.uuid4')
    @patch('query.lib.db.database.JobStatus')
    def test_create_async_query_endpoint(self, mock_job_status, mock_uuid, mock_sqs_client):
        mock_uuid.return_value = 1234
        query = "SELECT * FROM FILES;"

        response = self.client.post("v1/query/async", data=json.dumps(query))
        self.assertEqual(mock_job_status.call_count, 1)
        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=Config.async_query_queue_url,
            MessageBody=json.dumps({"query": query, "job_id": "1234"})
        )
        self.assertEqual(json.loads(response.data), {'query': query, "job_id": '1234'})

    @patch('query.lib.db.database.JobStatus')
    def test_get_async_query_status_when_job_doesnt_exist(self, mock_job_status):
        mock_job_status().select.return_value = None
        response = self.client.get("v1/query/async/3d8608c3-0ca6-430a-9f90-2117be6af160")
        self.assertEqual(response.status_code, 404)

    @patch('query.lib.db.database.JobStatus')
    def test_get_async_query_status_when_job_is_not_complete(self, mock_job_status):
        mock_job_status().select.return_value = {'uuid': self.uuid, 'status': 'PROCESSING'}
        response = self.client.get(f"v1/query/async/{self.uuid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'job_id': self.uuid, 'status': 'PROCESSING'})

    @patch('query.lib.db.database.JobStatus')
    @patch('query.lambdas.api_server.v1.endpoints.s3_client')
    def test_get_async_query_status_when_job_is_complete(self, mock_s3, mock_job_status):
        mock_s3.generate_presigned_url.return_value = 'www.ThisUrlShouldWork.com'
        mock_job_status().select.return_value = {'uuid': self.uuid, 'status': 'COMPLETE'}
        response = self.client.get(f"v1/query/async/{self.uuid}")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(json.loads(response.data), {
            'job_id': self.uuid,
            'status': 'COMPLETE',
            'presigned_url': 'www.ThisUrlShouldWork.com'})
