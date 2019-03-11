import os, sys, json, logging, getpass

from dcplib.aws_secret import AwsSecret
import sqlalchemy
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class ConfigFactory:
    app_name = os.environ["APP_NAME"]
    app = None
    stage = os.environ["STAGE"]
    bundle_events_queue_name = os.environ["BUNDLE_EVENTS_QUEUE_NAME"]
    async_queries_queue_name = os.environ["ASYNC_QUERIES_QUEUE_NAME"]
    s3_bucket_name = os.environ["SERVICE_S3_BUCKET"]

    try:
        import chalice.local
        local_mode = True
    except ImportError:
        local_mode = False

    db_statement_timeout = 20
    _db = None
    _db_session_factory = None
    _db_sessions = {}
    _webhook_keys = None
    _db_engine_params = {
        "echo": True,
        "connect_args": {"options": ""}
    }
    _readonly_db = True

    @property
    def webhook_keys(self):
        if self._webhook_keys is None:
            secret = AwsSecret(f"{self.app}/{self.stage}/webhook-auth-config")
            self._webhook_keys = json.loads(secret.value)["hmac_keys"]
        return self._webhook_keys

    @property
    def db(self):
        if self._db is None:
            connect_opts = " -c statement_timeout={}".format(self.db_statement_timeout)
            self._db_engine_params["connect_args"]["options"] += connect_opts
            if self.local_mode:
                db_user = getpass.getuser()
                db_password = ""
                db_host = "localhost"
                db_name = getpass.getuser()
            else:
                db_user = AwsSecret(f"{self.app_name}/{os.environ['STAGE']}/db/username").value.strip()
                db_password = AwsSecret(f"{self.app_name}/{os.environ['STAGE']}/db/password").value.strip()
                if self._readonly_db:
                    db_host = AwsSecret(f"{self.app_name}/{os.environ['STAGE']}/db/readonly_hostname").value.strip()
                else:
                    db_host = AwsSecret(f"{self.app_name}/{os.environ['STAGE']}/db/hostname").value.strip()
                db_name = self.app_name
            self._db = sqlalchemy.create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}",
                                                **self._db_engine_params)
        return self._db

    @property
    def db_session(self):
        if self._db_session_factory is None:
            self._db_session_factory = sessionmaker(bind=self.db)
        if id(self.app.current_request) not in self._db_sessions:
            self._db_sessions.clear()
            self._db_sessions[id(self.app.current_request)] = self._db_session_factory()
        return self._db_sessions[id(self.app.current_request)]
