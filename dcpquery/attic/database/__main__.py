from query.lib.config import Config
from . import Database

Database(Config.serve_db_uri).init_db()
