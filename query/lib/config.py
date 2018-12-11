import os
import json

from dcplib.aws_secret import AwsSecret

from query.lib.logger import logger


def _get(d, name: str, sensitive: bool = False, default=None) -> str:
    sensitive_display = '*' * 20
    try:
        value = d[name]
        display_value = sensitive_display if sensitive else value
        logger.info(f"LOADED CONF VARIABLE: {name}=\"{display_value}\"")

        return value
    except KeyError as e:
        display_value = sensitive_display if sensitive else default
        if default:
            logger.info(f"SET DEFAULT CONF VARIABLE: {name}=\"{display_value}\"")
            return default
        logger.error(f"Required parameter \"{name}\" is not set!")
        raise e


class Config:

    def __setattr__(self, attr, value):
        if hasattr(self, attr):
            raise Exception("Attempting to alter read-only value")

        self.__dict__[attr] = value

    deployment_stage = _get(os.environ, 'DEPLOYMENT_STAGE')

    _secret = json.loads(AwsSecret(f"dcp/query/{deployment_stage}/database").value)

    _pg_bouncer_dns_name = _get(_secret, 'pgbouncer_dns_name')
    _database_name = _get(_secret, 'database')
    _user = _get(_secret, 'user', sensitive=True)
    _password = _get(_secret, 'password', sensitive=True)

    # TODO: automate creation of test database
    _database_uri_prefix = f"postgresql://{_user}:{_password}@{_pg_bouncer_dns_name}:5432/"
    test_database_uri = _database_uri_prefix + "test"
    serve_database_uri = _database_uri_prefix + _database_name

    admin_mode = _get(os.environ, 'ADMIN_MODE', default="0") == "1"


def requires_admin_mode(function_to_wrap):
    def call(*args, **kwargs):
        if not Config.admin_mode:
            raise Exception("Admin mode is not enabled! Enable with `ADMIN_MODE=1`")
        result = function_to_wrap(*args, **kwargs)
        return result
    return call
