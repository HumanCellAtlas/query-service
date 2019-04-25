import os, sys, json, logging, getpass, typing, threading

from dcplib.aws_secret import AwsSecret
import sqlalchemy
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class DCPQueryConfig:
    app_name = os.environ["APP_NAME"]
    app = None
    stage = os.environ["STAGE"]
    dss_host = os.environ["DSS_HOST"]
    bundle_events_queue_name = os.environ["BUNDLE_EVENTS_QUEUE_NAME"]
    async_queries_queue_name = os.environ["ASYNC_QUERIES_QUEUE_NAME"]
    s3_bucket_name = os.environ["SERVICE_S3_BUCKET"]
    webhook_secret_name = os.environ["WEBHOOK_SECRET_NAME"]

    API_GATEWAY_MAX_RESULT_SIZE = 8 * 1024 * 1024
    S3_SINGLE_UPLOAD_MAX_SIZE = 64 * 1024 * 1024

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
        "connect_args": {"options": ""},
        "implicit_returning": False
    }
    _readonly_db = True

    @property
    def webhook_keys(self):
        if self._webhook_keys is None:
            secret = AwsSecret(self.webhook_secret_name)
            self._webhook_keys = json.loads(secret.value)["hmac_keys"]
        return self._webhook_keys

    def reset_db_timeout_seconds(self, timeout_seconds):
        if self.db_statement_timeout_seconds != timeout_seconds:
            self.db_statement_timeout_seconds = timeout_seconds
            self.reset_db_session()

    def reset_db_session(self):
        self._db = None
        self._db_session_factory = None
        self._db_sessions.clear()

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
