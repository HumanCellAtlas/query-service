import os, sys, re, json, collections, logging, datetime, uuid
from decimal import Decimal

import requests, connexion, chalice
from sqlalchemy.engine.result import RowProxy
from connexion.resolver import RestyResolver
from connexion.lifecycle import ConnexionResponse


class JSONEncoder(json.JSONEncoder):
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
        with self.connexion_app.app.test_request_context(path=path,
                                                         base_url=base_url,
                                                         query_string=self.current_request.query_params,
                                                         method=self.current_request.method,
                                                         headers=list(self.current_request.headers.items()),
                                                         data=req_body,
                                                         environ_base=self.current_request.stage_vars):
            flask_res = self.connexion_app.app.full_dispatch_request()
        res_headers = dict(flask_res.headers)
        res_headers.pop("Content-Length", None)
        res_body = b"".join([c for c in flask_res.response]).decode()
        return chalice.Response(status_code=flask_res._status_code, headers=res_headers, body=res_body)


class ChaliceWithLoggingConfig(chalice.Chalice):
    silence_debug_loggers = ["botocore"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig()
        if int(os.environ.get("DEBUG", "0")) == 0:
            self.debug = False
        elif int(os.environ.get("DEBUG", "0")) == 1:
            self.debug = True
            logging.root.setLevel(logging.INFO)
        elif int(os.environ.get("DEBUG", "0")) > 1:
            self.debug = True
            logging.root.setLevel(logging.DEBUG)
            for logger_name in self.silence_debug_loggers:
                logging.getLogger(logger_name).setLevel(logging.INFO)


class DCPQueryServer(ChaliceWithConnexion, ChaliceWithLoggingConfig):
    pass
