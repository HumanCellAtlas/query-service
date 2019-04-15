import os, sys, json, logging, getpass, typing, threading

from dcplib.aws_secret import AwsSecret
import sqlalchemy
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class DCPQueryConfig:
    app_name = os.environ["APP_NAME"]
    app = None
    stage = os.environ["STAGE"]
    bundle_events_queue_name = os.environ["BUNDLE_EVENTS_QUEUE_NAME"]
    async_queries_queue_name = os.environ["ASYNC_QUERIES_QUEUE_NAME"]
    s3_bucket_name = os.environ["SERVICE_S3_BUCKET"]
    webhook_secret_name = os.environ["WEBHOOK_SECRET_NAME"]

    try:
        import chalice.local
        local_mode = True
    except ImportError:
        local_mode = False

    db_statement_timeout_seconds = 20
    _db = None
    _db_session_factory = None
    _db_sessions: typing.Dict[int, typing.Any] = {}
    _webhook_keys = None
    _db_engine_params = {
        "echo": True,
        "connect_args": {"options": ""}
    }
    _readonly_db = True
    _db_ignore_insert_conflicts = True

    @property
    def webhook_keys(self):
        if self._webhook_keys is None:
            secret = AwsSecret(self.webhook_secret_name)
            self._webhook_keys = json.loads(secret.value)["hmac_keys"]
        return self._webhook_keys

    @property
    def db(self):
        if self._db is None:
            connect_opts = " -c statement_timeout={}s".format(self.db_statement_timeout_seconds)
            self._db_engine_params["connect_args"]["options"] += connect_opts
            if self.local_mode:
                db_user = getpass.getuser()
                db_password = ""
                db_host = ""
            else:
                db_user = AwsSecret(f"{self.app_name}/{os.environ['STAGE']}/postgresql/username").value.strip()
                db_password = AwsSecret(f"{self.app_name}/{os.environ['STAGE']}/postgresql/password").value.strip()
                if self._readonly_db:
                    db_host_secret_name = f"{self.app_name}/{os.environ['STAGE']}/postgresql/readonly_hostname"
                else:
                    db_host_secret_name = f"{self.app_name}/{os.environ['STAGE']}/postgresql/hostname"
                db_host = AwsSecret(db_host_secret_name).value.strip()
            db_name = self.app_name
            self._db = sqlalchemy.create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}",
                                                **self._db_engine_params)

            if self._db_ignore_insert_conflicts:
                @sqlalchemy.event.listens_for(self._db, 'before_cursor_execute', retval=True)
                def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                    if statement.startswith("INSERT"):
                        if "RETURNING" in statement:
                            statement.replace("RETURNING", "ON CONFLICT DO NOTHING RETURNING")
                        else:
                            statement += " ON CONFLICT DO NOTHING"
                    return statement, parameters

        return self._db

    @property
    def db_session(self):
        if self._db_session_factory is None:
            self._db_session_factory = sessionmaker(bind=self.db)
        session_id = id(self.app.current_request) if self.app else threading.get_ident()
        if session_id not in self._db_sessions:
            self._db_sessions.clear()
            self._db_sessions[session_id] = self._db_session_factory()
        return self._db_sessions[session_id]
