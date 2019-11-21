#!/usr/bin/env python3.6

import json
import unittest
from contextlib import contextmanager

from unittest.mock import patch

import requests
from requests_http_signature import HTTPSignatureAuth

from dcpquery import config
from dcpquery.api.files.schema_type import get_file_fqids_for_schema_type_version
from tests import fast_query_mock_result, fast_query_expected_results
from tests.unit import TestChaliceApp, DCPAssertMixin, DCPQueryUnitTest


class TestEndpoints(TestChaliceApp, DCPQueryUnitTest):
    def setUp(self):
        super().setUp()
        self.uuid = "3d8608c3-0ca6-430a-9f90-2117be6af160"

    def test_healthcheck_endpoint(self):
        response = self.app.get("/internal/health")
        self.assertEqual(response.status_code, 200)

    def test_query_endpoint(self):
        query = "select * from files limit 10"
        res = self.assertResponse("POST", "/v1/query", requests.codes.ok, {"query": query})
        self.assertEqual(len(res.json['results']), 10)

    def test_query_endpoint_with_params(self):
        query = "select * from files where size > %(s)s limit 10"
        params = {"s": 0}
        res = self.assertResponse("POST", "/v1/query", requests.codes.ok, {"query": query, "params": params})
        self.assertEqual(len(res.json['results']), 10)

    def test_query_endpoint_redirects_timeouts(self):
        with manage_query_timeout(3):
            query = "select pg_sleep(5); select * from files limit 10"
            self.assertResponse("POST", "/v1/query", requests.codes.found, {"query": query})

    def test_query_endpoint_redirects_too_large_responses(self):
        config.API_GATEWAY_MAX_RESULT_SIZE = 10
        query = "select * from files"
        self.assertResponse("POST", "/v1/query", requests.codes.found, {"query": query})
        config.API_GATEWAY_MAX_RESULT_SIZE = 8 * 1024 * 1024

    @patch('dcplib.aws.resources.sqs.Queue')
    def test_webhook_endpoint(self, mock_sqs_queue):
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
        config._webhook_keys = {"foo": "bar"}
        signer = HTTPSignatureAuth(key_id="foo", key=b"bar")
        req = signer(requests.Request("POST", "http://localhost/bundles/event", json=subscription_data).prepare())
        self.assertResponse(req.method, "/bundles/event", headers=req.headers, data=req.body,
                            expected_code=requests.codes.accepted)
        mock_sqs_queue().send_message.assert_called_once_with(MessageBody=json.dumps(subscription_data))

    @unittest.skip("WIP")
    @patch('query.lambdas.api_server.v1.endpoints.sqs_client')
    @patch('query.lambdas.api_server.v1.endpoints.uuid4')
    @patch('query.lib.db.database.JobStatus')
    def test_create_async_query_endpoint(self, mock_job_status, mock_uuid, mock_sqs_client):
        mock_uuid.return_value = 1234
        query = "SELECT * FROM FILES;"

        response = self.client.post("v1/query/async", data=json.dumps(query))
        self.assertEqual(mock_job_status.call_count, 1)
        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=config.async_query_queue_url,
            MessageBody=json.dumps({"query": query, "job_id": "1234"})
        )
        self.assertEqual(json.loads(response.data), {'query': query, "job_id": '1234'})

    @unittest.skip("WIP")
    @patch('query.lib.db.database.JobStatus')
    def test_get_async_query_status_when_job_doesnt_exist(self, mock_job_status):
        mock_job_status().select.return_value = None
        response = self.client.get("v1/query/async/3d8608c3-0ca6-430a-9f90-2117be6af160")
        self.assertEqual(response.status_code, 404)

    @unittest.skip("WIP")
    @patch('query.lib.db.database.JobStatus')
    def test_get_async_query_status_when_job_is_not_complete(self, mock_job_status):
        mock_job_status().select.return_value = {'uuid': self.uuid, 'status': 'PROCESSING'}
        response = self.client.get(f"v1/query/async/{self.uuid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'job_id': self.uuid, 'status': 'PROCESSING'})

    @unittest.skip("WIP")
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

    def test_get_file_fqids_for_schema_type_version(self):
        file_info = config.db_session.execute("""
                                              SELECT dcp_schema_type_name, schema_major_version, schema_minor_version
                                              FROM files LIMIT 1;
                                              """).fetchall()[0]
        schema_type = file_info[0]
        major = file_info[1]
        minor = file_info[2]
        expected_file_fqids = [x[0] for x in config.db_session.execute("""
          SELECT fqid
          FROM files_all_versions
          WHERE dcp_schema_type_name=:schema_type
          AND schema_major_version=:major_version
          AND schema_minor_version=:minor_version
          """, {"schema_type": schema_type, "major_version": major, "minor_version": minor}).fetchall()]
        file_fqids = get_file_fqids_for_schema_type_version(schema_type=schema_type, major=major, minor=minor)
        self.assertCountEqual(file_fqids, expected_file_fqids)

    def test_get_bundle_fqids_for_file_endpoint(self):
        file_uuid = str(config.db_session.execute("SELECT uuid from files limit 1").fetchall()[0][0])
        expected_bundle_fqids = [x[0] for x in config.db_session.execute(f"""
          SELECT bundle_fqid FROM bundle_file_links WHERE file_fqid in (
          SELECT fqid from files_all_versions where uuid='{file_uuid}')
          """).fetchall()]
        response = self.assertResponse(
            "GET",
            f"/v1/files/{file_uuid}/bundles?check_events=false",
            requests.codes.ok,
        )

        self.assertEqual(sorted(expected_bundle_fqids), sorted(response.json['bundle_fqids']))

    def test_get_bundle_fqids_for_file_that_doesnt_exist(self):
        file_uuid = "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
        self.assertResponse(
            "GET",
            f"/v1/files/{file_uuid}/bundles?check_events=false",
            requests.codes.not_found,
        )

    def test_get_file_fqids_for_schema_type_that_doesnt_exist(self):
        schema_type = 'non_existent'
        major = 0
        minor = 0
        self.assertResponse(
            "GET",
            f"/v1/files/schema/{schema_type}?version={str(major)}.{str(minor)}",
            requests.codes.not_found,
        )

    def test_get_file_fqids_for_schema_type_endpoint(self):
        schema_information = config.db_session.execute(
            "SELECT dcp_schema_type_name, schema_major_version, schema_minor_version FROM files LIMIT 1;"
        ).fetchall()[0]
        schema_type = schema_information[0]
        major = schema_information[1]
        minor = schema_information[2]

        expected_file_fqids = [x[0] for x in config.db_session.execute("""
                  SELECT fqid
                  FROM files_all_versions
                  WHERE dcp_schema_type_name=:schema_type
                  AND schema_major_version=:major_version
                  AND schema_minor_version=:minor_version
                  """, {"schema_type": schema_type, "major_version": major, "minor_version": minor}).fetchall()]

        response = self.assertResponse(
            "GET",
            f"/v1/files/schema/{schema_type}?version={str(major)}.{str(minor)}",
            requests.codes.ok,
        )
        self.assertEqual(sorted(expected_file_fqids), sorted(response.json['file_fqids']))


@contextmanager
def manage_query_timeout(timeout_seconds):
    config.reset_db_timeout_seconds(timeout_seconds)
    try:
        yield
    finally:
        config.reset_db_timeout_seconds(20)


if __name__ == '__main__':
    unittest.main()
