from __future__ import with_statement

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this line is necessary to allow for imports from dcpquery
sys.path.insert(0, os.getcwd())

from dcpquery.db.models import SQLAlchemyBase  # noqa
from dcpquery import config as dcpquery_config  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

alembic_config = context.config

# Interpret the config file for Python logging.
fileConfig(alembic_config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = SQLAlchemyBase.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = dcpquery_config.db_url
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    with dcpquery_config.db.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
