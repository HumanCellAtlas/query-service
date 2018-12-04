import unittest
from unittest.mock import Mock, patch
from lambdas.load_data import load_data


class TestEndpoints(unittest.TestCase):
    def setUp(self):
        self.data_loader = load_data.LoadData()

    def test_query_service_data_load(self):
        load_data.extractor = 'foo'
        load_data.loader = 'bah'
        self.data_loader.extract_transform_load = Mock()
        mock_event_data = {"Records": [{'messageId': '33b4de0b-274a-48f0-9b5c-ee600b439c6c',
                                        'receiptHandle': 'AQEBm6V306aUkJhPlCT2hcBz9Q1QXmNmqPV4UC/ebmGQYAMLKQoHxn2kLEw3+XR2JuxuKc09ccsmdJ25sV65rGYI4UCb6kMg9cBGZ0w+MdU+GDpq0tKdqGzJV7i6VDBB5pCp5X7bbTGrQDwlVFb8/yZ++Ps52zB6E+kCIUH2H6V+xq+Wjc0FDNj7nXBoWylKQsiiS3jBHiq4sRrZEzDrv7vy/Pjg/ibbhvNf1um8t1Wpwo/McQgMRjwgE3PuPveJtUH8aO41XI4J9oEHjm9FgmwahZyY+UKRM9fBD/dkKEiGS09TYjRL9zcOGsCJB/95lr/cb6UszZJlgf7W50XWGg7c/OIek69BjGCskgsZn/JVYHQ9678k7U6zhI1S639vnrvfVF44FWhX0fMmHAhuIUlI0w==',
                                        'body': '{"bundle_uuid": "9a5cbcbd-866c-4b6a-9fdb-6581a2d47f3c", "bundle_version": "2018-11-27T211302.714868Z"}',
                                        'attributes': {'ApproximateReceiveCount': '1',
                                                       'SentTimestamp': '1543357453729',
                                                       'SenderId': 'AROAIW2WQHOU5B2TZ546I:query-api-dev',
                                                       'ApproximateFirstReceiveTimestamp': '1543357453745'},
                                        'messageAttributes': {}, 'md5OfBody': '4bcabebd5f583eb0b964841edbf3a3ca',
                                        'eventSource': 'aws:sqs',
                                        'eventSourceARN': 'arn:aws:sqs:us-east-1:861229788715:dcp-query-data-input-queue-dev',
                                        'awsRegion': 'us-east-1'}]}
        self.data_loader.query_service_data_load(mock_event_data, 'context')
        self.data_loader.extract_transform_load.assert_called_once_with(extractor='foo', loader='bah',
            bundle_uuid='9a5cbcbd-866c-4b6a-9fdb-6581a2d47f3c', bundle_version='2018-11-27T211302.714868Z'
        )

    @patch('query.lambdas.load_data.load_data.BundleDocumentTransform.transform')
    def test_extract_transform_load(self, mock_transform):
        mock_transform.return_value = 'TRANSFORMED BUNDLE'
        load_data.extractor = Mock()
        load_data.loader = Mock()
        load_data.extractor.extract_bundle.return_value = 'BUNDLE'
        self.data_loader.extract_transform_load(load_data.extractor, load_data.loader, 'UUID', 'VERSION')
        load_data.extractor.extract_bundle.assert_called_once_with('UUID', 'VERSION')
        mock_transform.assert_called_once_with('BUNDLE')
        load_data.loader.load.assert_called_once_with('BUNDLE', 'TRANSFORMED BUNDLE')
