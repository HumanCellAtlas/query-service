from query.lib.common.logging import get_logger
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase

logger = get_logger('query.lambdas.load_data.load_data')


class LoadData:
    def query_service_data_load(self, event, context):
        logger.info(f"YOU ARE HERE EVENT: {event}, CONTEXT: {context}")
        db = PostgresDatabase(Config.serve_database_uri)
        cursor = db._connection.cursor()

        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
              AND table_schema = 'public';
            """
        )
        response = cursor.fetchall()
        logger.info(f"QUERIED DB: {response}")
        return 3


{'notification': {'transaction_id': 'c1c63054-b79d-4fbb-8f0e-057af10a20d7',
                  'subscription_id': '1168f336-bc0d-4f64-8d79-746f1085cc3b', 'es_query': {'query': {
        'bool': {'must_not': [{'term': {'admin_deleted': True}}],
                 'must': [{'exists': {'field': 'files.donor_organism_json'}},
                          {'range': {'manifest.version': {'gte': '2018-10-10'}}}]}}},
                  'match': {'bundle_uuid': '00a58b6a-0f49-441a-b7cd-269403709752',
                            'bundle_version': '2018-11-15T224541.831728Z'}}
