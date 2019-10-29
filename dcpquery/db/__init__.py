"""
This module provides a SQLAlchemy-based database schema for the DCP Query Service.
"""
import logging

from sqlalchemy import (exc as sqlalchemy_exceptions)

from .. import config
from ..exceptions import DCPQueryError, QueryTimeoutError

logger = logging.getLogger(__name__)


def drop_db(dry_run=True):
    from sqlalchemy_utils import database_exists, drop_database
    if database_exists(config.db.url):
        if dry_run:
            logger.critical("Would drop database %s", config.db.url)
        else:
            logger.critical("About to drop database %s", config.db.url)
            drop_database(config.db.url)
            logger.critical("Dropped database %s", config.db.url)


def init_db(dry_run=True):
    from sqlalchemy_utils import database_exists, create_database

    logger.info("Initializing database at %s", repr(config.db.url))
    if not database_exists(config.db.url):
        logger.info("Creating database")
        create_database(config.db.url)
    logger.info("Initializing database")
    if dry_run:
        orig_db_engine_params = dict(config._db_engine_params)
        config._db_engine_params.update(strategy="mock", executor=lambda sql, *args, **kwargs: print(sql))
    migrate_db()
    if dry_run:
        config._db_engine_params = orig_db_engine_params
        config.reset_db_session()


def migrate_db():
    import alembic.command
    logger.info("Migrating database at %s", repr(config.db.url))
    alembic.command.upgrade(config.alembic_config, "head")


def run_query(query, params, rows_per_page=100):
    try:
        cursor = config.db.execute(query, params)
        while True:
            rows = cursor.fetchmany(size=rows_per_page)
            for row in rows:
                yield row
            if not rows:
                break
    except (sqlalchemy_exceptions.InternalError, sqlalchemy_exceptions.ProgrammingError) as e:
        raise DCPQueryError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
    except sqlalchemy_exceptions.OperationalError as e:
        if "canceling statement due to statement timeout" in str(e):
            raise QueryTimeoutError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
        else:
            raise


def commit_to_db(arg):
    config.db_session.commit()
