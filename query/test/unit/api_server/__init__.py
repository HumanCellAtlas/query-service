import os
import yaml

import connexion


def client_for_test_api_server():
    flask_app = connexion.FlaskApp(__name__)

    swagger_yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../config/query-api.yml'))
    with open(swagger_yaml_path, mode='rb') as swagger_yaml:
        contents = swagger_yaml.read()
        swagger_string = contents.decode()
        specification = yaml.safe_load(swagger_string)  # type: dict
    specification['host'] = 'localhost'
    flask_app.add_api(specification)

    return flask_app.app.test_client()
