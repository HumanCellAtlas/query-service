import os, sys, json, re, unittest, functools, typing, collections, pprint, time

import requests
from chalice.cli import CLIFactory
from chalice.local import LocalGateway, LocalGatewayException
from furl import furl
from flask import wrappers
from dcplib.test_helpers import DCPAssertMixin


class ChaliceTestHarness:
    def __init__(self):
        project_dir = os.path.join(os.path.dirname(__file__), "..", "..")
        config = CLIFactory(project_dir=project_dir).create_config_obj(chalice_stage_name="dev")
        self._chalice_app = config.chalice_app
        self._gateway = LocalGateway(self._chalice_app, config)

    @functools.lru_cache(maxsize=64, typed=False)
    def __getattr__(self, method):
        return functools.partial(self.request, method=method.upper())

    def request(self, path, headers={}, data={}, method="GET"):
        headers.setdefault("host", "localhost")
        if isinstance(data, dict):
            data = json.dumps(data)
        resp_obj = requests.Response()
        try:
            response = self._gateway.handle_request(method, path, headers, data)
        except LocalGatewayException as error:
            resp_obj.status_code = error.CODE
            resp_obj.headers = error.headers
            resp_obj._content = error.body
        else:
            resp_obj.status_code = response['statusCode']
            resp_obj.headers = response['headers']
            resp_obj._content = response['body']
        resp_obj.encoding = "utf-8"
        if not isinstance(resp_obj._content, bytes):
            resp_obj._content = resp_obj._content.encode()
        resp_obj.headers['Content-Length'] = str(len(resp_obj.content))
        return resp_obj


class TestChaliceApp(unittest.TestCase, DCPAssertMixin):
    def setUp(self):
        self.app = ChaliceTestHarness()

    def test_root_route(self):
        res = self.app.get('/')
        res.raise_for_status()
        self.assertEqual(res.status_code, requests.codes.ok)
