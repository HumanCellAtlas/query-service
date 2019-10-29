from dcpquery import config
from dcpquery.db.models import DCPMetadataSchemaType


def update_bundles_materialized_view():
    config.db_session.execute(
        """
        REFRESH MATERIALIZED VIEW CONCURRENTLY bundles
        """
    )


def update_files_materialized_view():
    config.db_session.execute(
        """
        REFRESH MATERIALIZED VIEW CONCURRENTLY files
        """
    )


def create_dcp_schema_type_materialized_views(matviews):
    schema_types = [schema[0] for schema in
                    config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()]
    for schema_type in schema_types:
        if schema_type not in matviews:
            config.db_session.execute(
                f"""
                  CREATE MATERIALIZED VIEW {schema_type} AS
                  SELECT f.* FROM files as f
                  WHERE f.dcp_schema_type_name = '{schema_type}'
                """
            )
            config.db_session.execute(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {schema_type+'_idx'} ON {schema_type} (fqid);

                """
            )
        else:
            config.db_session.execute(
                f"""
                REFRESH MATERIALIZED VIEW CONCURRENTLY {schema_type}
                """
            )


def create_materialized_view_tables():
    matviews = [x[0] for x in config.db_session.execute("SELECT matviewname FROM pg_catalog.pg_matviews;").fetchall()]
    config.reset_db_timeout_seconds(880)
    update_bundles_materialized_view()
    update_files_materialized_view()
    create_dcp_schema_type_materialized_views(matviews)
    config.db_session.commit()
