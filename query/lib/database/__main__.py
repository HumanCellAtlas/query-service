from . import Database

## ToDo dont hard code db_string, use config
db_string = 'postgresql://predev:example64@query-predev.cluster-cdaogjt23uha.us-east-1.rds.amazonaws.com:5432/query_predev'

Database(db_string).init_db()
