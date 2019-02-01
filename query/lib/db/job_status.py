import typing
from uuid import UUID

from query.lib.model import datetime_to_version
from query.lib.config import requires_admin_mode
from query.lib.db.table import Table


class JobStatus(Table):

    def insert(self, uuid: UUID) -> int:
        self._cursor.execute(
            """
            INSERT INTO job_status (job_id, status)
            VALUES (%s, %s)
            """,
            (
                str(uuid),
                'CREATED'
            )
        )
        result = self._cursor.rowcount
        return result

    def select(self, uuid: UUID) -> typing.Optional[dict]:
        self._cursor.execute(
            """
            SELECT * FROM job_status
            WHERE job_id = %s
            """,
            (
                str(uuid),
            )
        )
        response = self._cursor.fetchall()
        assert(len(response) <= 1)
        if len(response) == 0:
            # check in main db to avoid race conditions with replicas
            response = self.select_from_write_db(uuid)
            return response
        return dict(
            uuid=response[0][0],
            created_at=datetime_to_version(response[0][1]),
            status=response[0][2]
        )

    def select_from_write_db(self, uuid: UUID) -> typing.Optional[dict]:
        self._cursor.execute(
            "SELECT * FROM job_status WHERE job_id = %s FOR UPDATE ",
            (
                str(uuid),
            )
        )
        response = self._cursor.fetchall()
        assert (len(response) <= 1)
        if len(response) == 0:
            return None
        return dict(
            uuid=response[0][0],
            created_at=datetime_to_version(response[0][1]),
            status=response[0][2]
        )

    def update_job_status(self, uuid: UUID, new_status: str) -> typing.Optional[dict]:
        self._cursor.execute(
            """
            UPDATE job_status
            SET status = %s
            WHERE job_id = %s
            """,
            (
                new_status,
                str(uuid),
            )
        )

    def delete_old_rows(self):
        self._cursor.execute(
            """
            DELETE FROM job_status WHERE created_at < NOW() - INTERVAL '90 days';
            """
        )

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TYPE job_status_enum AS ENUM ('CREATED', 'PROCESSING', 'COMPLETE', 'FAILED');
            CREATE TABLE IF NOT EXISTS job_status (
                job_id UUID,
                created_at TIMESTAMP DEFAULT NOW(),
                status job_status_enum NOT NULL,
                PRIMARY KEY (job_id)
            );
        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS job_status; DROP TYPE IF EXISTS job_status_enum;")
