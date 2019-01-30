from query.lib.config import Config
from query.lib.db.database import PostgresDatabase

db = PostgresDatabase(Config.serve_database_uri)


def handler(event, context):
    with db.transaction() as (_, tables):
        tables.job_status.delete_old_rows()
