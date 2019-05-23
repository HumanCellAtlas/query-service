# `dcpquery/alembic`
This directory contains the configuration files for the [Alembic](https://alembic.sqlalchemy.org/en/latest/)
database migration tool. See the [Query Service Migrations documentation](../../docs/migrations.md) for more
information about creating and applying migrations.


| File/Directory name    |      Purpose      |
|:-----------------------|:------------------|
| versions/ |  Contains the migration files for the project | 
| env.py |    Configuration information for alembic, in particular connecting the SQLAlchemyBase to allow for autogeneration of migrations based on changes made to the Sqlalchemy ORM.   |
| script.py.mako | Outline for the generated migration files |
