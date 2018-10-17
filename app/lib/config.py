import os
import json
from lib.logger import logger
from dcplib.aws_secret import AwsSecret


def _get(d, name: str, sensitive: bool = False, default=None) -> str:
    try:
        value = d[name]
        display_value = '*' * 20 if sensitive else value
        logger.info(f"LOADED ENV_VARIABLE name=\"{name}\" value=\"{display_value}\"")
        return value
    except KeyError as e:
        logger.error(f"Required parameter \"{name}\" is not set!")
        if default:
            return default
        raise e


class Config:
    deployment_stage = _get(os.environ, 'DEPLOYMENT_STAGE')

    _secret = json.loads(AwsSecret(f"dcp/query/{deployment_stage}/database").value)

    _pg_bouncer_dns_name = _get(_secret, 'pgbouncer_dns_name')
    _rds_dns_name = _get(_secret, 'rds_dns_name')
    _database_name = _get(_secret, 'database')
    _user = _get(_secret, 'user', sensitive=True)
    _password = _get(_secret, 'password', sensitive=True)

    # TODO: automate creation of test database
    _database_uri_prefix = f"postgresql://{_user}:{_password}@{_pg_bouncer_dns_name}:5432/"
    test_database_uri = _database_uri_prefix + "test"
    serve_database_uri = _database_uri_prefix + _database_name
