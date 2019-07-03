import os, sys, re, json, collections, logging, datetime, uuid, gzip
from decimal import Decimal

import requests, connexion, chalice, brotli
from sqlalchemy.engine.result import RowProxy
from connexion.resolver import RestyResolver
from connexion.lifecycle import ConnexionResponse
from werkzeug.http import parse_accept_header


class JSONEncoder(json.JSONEncoder):
    """
    This JSON encoder subclass is inserted into the Connexion/Flask app instance so it can encode response bodies.

    Unlike the default JSON encoder, it knows how to serialize datetime, UUID, and SQLAlchemy RowProxy objects.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            if o.tzinfo:
                # eg: '2015-09-25T23:14:42.588601+00:00'
                return o.isoformat('T')
            else:
                # No timezone present - assume UTC.
                # eg: '2015-09-25T23:14:42.588601Z'
                return o.isoformat('T') + 'Z'

        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, uuid.UUID):
            return str(o)

        if isinstance(o, RowProxy):
            return dict(o)

        if isinstance(o, Decimal):
            return float(o)

        return json.JSONEncoder.default(self, o)


class ChaliceWithConnexion(chalice.Chalice):
    """
    Subclasses Chalice to host a Connexion app, route and proxy requests to it.
    """
    def __init__(self, swagger_spec_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.swagger_spec_path = swagger_spec_path
        self.connexion_app = self.create_connexion_app()
        self.trailing_slash_routes = []
        routes = collections.defaultdict(list)
        for rule in self.connexion_app.app.url_map.iter_rules():
            route = re.sub(r"<(.+?)(:.+?)?>", r"{\1}", rule.rule)
            if route.endswith("/"):
                self.trailing_slash_routes.append(route.rstrip("/"))
            routes[route.rstrip("/")] += rule.methods
        for route, methods in routes.items():
            self.route(route, methods=list(set(methods) - {"OPTIONS"}), cors=True)(self.dispatch)

    def create_connexion_app(self):
        app = connexion.App(self.app_name)
        app.app.json_encoder = JSONEncoder
        resolver = RestyResolver(self.app_name + '.api', collection_endpoint_name="list")
        app.add_api(self.swagger_spec_path, resolver=resolver, validate_responses=True, arguments=os.environ)
        return app

    def dispatch(self, *args, **kwargs):
        uri_params = self.current_request.uri_params or {}
        path = self.current_request.context["resourcePath"].format(**uri_params)
        if self.current_request.context["resourcePath"] in self.trailing_slash_routes:
            if self.current_request.context["path"].endswith("/"):
                path += "/"
            else:
                return chalice.Response(status_code=requests.codes.found, headers={"Location": path + "/"}, body="")
        req_body = self.current_request.raw_body if self.current_request._body is not None else None
        base_url = "https://{}".format(self.current_request.headers["host"])
        query_string = self.current_request.query_params or {}
        with self.connexion_app.app.test_request_context(path=path,
                                                         base_url=base_url,
                                                         query_string=list(query_string.items()),
                                                         method=self.current_request.method,
                                                         headers=list(self.current_request.headers.items()),
                                                         data=req_body,
                                                         environ_base=self.current_request.stage_vars):
            flask_res = self.connexion_app.app.full_dispatch_request()
        res_headers = dict(flask_res.headers)
        res_headers.pop("Content-Length", None)
        res_body = b"".join([c for c in flask_res.response])
        return chalice.Response(status_code=flask_res._status_code, headers=res_headers, body=res_body)


class ChaliceWithRequestLogging(chalice.Chalice):
    def _get_view_function_response(self, view_function, function_args):
        uri_params = self.current_request.uri_params or {}
        path_pattern = self.current_request.context["resourcePath"]
        path = path_pattern.format(**uri_params)
        method = self.current_request.method
        query_params = self.current_request.query_params
        source_ip = self.current_request.context['identity']['sourceIp']
        content_length = self.current_request.headers.get('content-length', '-')
        user_agent = self.current_request.headers.get('user-agent')
        self.log.info('[req] "%s %s" %s %s "%s" %s', method, path, source_ip, content_length, user_agent, query_params)
        res = super()._get_view_function_response(view_function, function_args)
        self.log.info('[res] %s', res.status_code)
        return res


class ChaliceWithGzipBinaryResponses(chalice.Chalice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api.binary_types.append('*/*')

    def _get_view_function_response(self, view_function, function_args):
        res = super()._get_view_function_response(view_function, function_args)
        if isinstance(res.body, dict):
            res.body = json.dumps(res.body)
        if not isinstance(res.body, bytes):
            res.body = res.body.encode()
        if "Content-Encoding" not in res.headers:
            accept_encoding = parse_accept_header(self.current_request.headers.get("Accept-Encoding"))
            if "br" in accept_encoding:
                res.body = brotli.compress(res.body, mode=brotli.MODE_TEXT, quality=5)
                res.headers["Content-Encoding"] = "br"
            elif "gzip" in accept_encoding:
                res.body = gzip.compress(res.body)
                res.headers["Content-Encoding"] = "gzip"
        return res


class DCPQueryServer(ChaliceWithConnexion, ChaliceWithRequestLogging, ChaliceWithGzipBinaryResponses):
    pass
