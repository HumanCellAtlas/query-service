import os, sys, json, unittest

from dcpquery.etl import process_bundle_event


class TestExtractor(unittest.TestCase):
    def test_bundle_event_handling(self):
        with open(f'{os.path.dirname(__file__)}/../fixtures/mock_sqs_bundle_create_event.json', 'r') as fh:
            process_bundle_event(json.loads(json.load(fh)["Records"][0]["body"]))

        with open(f'{os.path.dirname(__file__)}/../fixtures/mock_sqs_bundle_delete_event.json', 'r') as fh:
            process_bundle_event(json.loads(json.load(fh)["Records"][0]["body"]))


if __name__ == '__main__':
    unittest.main()
