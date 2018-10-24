import os
import unittest

from moto import mock_iam

os.environ['DEPLOYMENT_STAGE'] = 'test'
os.environ['LOG_LEVEL'] = 'CRITICAL'


class EnvironmentSetup:
    """
    Set environment variables.
    Provide a dict of variable names and values.
    Setting a value to None will delete it from the environment.
    """
    def __init__(self, env_vars_dict):
        self.env_vars = env_vars_dict
        self.saved_vars = {}

    def enter(self):
        for k, v in self.env_vars.items():
            if k in os.environ:
                self.saved_vars[k] = os.environ[k]
            if v:
                os.environ[k] = v
            else:
                if k in os.environ:
                    del os.environ[k]

    def exit(self):
        for k, v in self.saved_vars.items():
            os.environ[k] = v

    def __enter__(self):
        self.enter()

    def __exit__(self, type, value, traceback):
        self.exit()


class QueryTestCaseUsingLiveAWS(unittest.TestCase):

    def setUp(self):
        # Does nothing but provide for consistency in test subclasses.
        pass

    def tearDown(self):
        # Does nothing but provide for consistency in test subclasses.
        pass


class QueryTestCaseUsingMockAWS(unittest.TestCase):

    def setUp(self):
        # Setup mock AWS
        self.iam_mock = mock_iam()
        self.iam_mock.start()

    def tearDown(self):
        self.iam_mock.stop()
