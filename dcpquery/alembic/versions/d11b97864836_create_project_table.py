"""create project table, link to files

Revision ID: d11b97864836
Revises: e5a3141a178d
Create Date: 2019-10-09 09:48:00.224115

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd11b97864836'
down_revision = 'e5a3141a178d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('projects_all_versions',
                    sa.Column('fqid', sa.String(), nullable=False),
                    sa.Column('uuid', postgresql.UUID(), nullable=False),
                    sa.Column('version', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('fqid')
                    )
    op.create_index(op.f('ix_projects_all_versions_fqid'), 'projects_all_versions', ['fqid'], unique=False)
    op.create_index(op.f('ix_projects_all_versions_uuid'), 'projects_all_versions', ['uuid'], unique=False)
    op.create_index(op.f('ix_projects_all_versions_version'), 'projects_all_versions', ['version'], unique=False)
    op.create_table('project_file_join_table',
                    sa.Column('project_fqid', sa.String(), nullable=False),
                    sa.Column('file_fqid', sa.String(), nullable=False),
                    sa.ForeignKeyConstraint(['file_fqid'], ['files_all_versions.fqid'], ),
                    sa.ForeignKeyConstraint(['project_fqid'], ['projects_all_versions.fqid'], ),
                    sa.PrimaryKeyConstraint('project_fqid', 'file_fqid'),
                    sa.UniqueConstraint('project_fqid', 'file_fqid', name='project_file_uc')
                    )
    op.create_index(op.f('ix_project_file_join_table_file_fqid'), 'project_file_join_table', ['file_fqid'],
                    unique=False)
    op.create_index(op.f('ix_project_file_join_table_project_fqid'), 'project_file_join_table', ['project_fqid'],
                    unique=False)
    op.execute(
        """
        CREATE OR REPLACE RULE project_table_ignore_duplicate_inserts AS
            ON INSERT TO projects_all_versions
                WHERE EXISTS (
                  SELECT 1
                FROM projects_all_versions
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE RULE project_file_join_table_ignore_duplicate_inserts AS
            ON INSERT TO project_file_join_table
                WHERE EXISTS (
                  SELECT 1
                FROM project_file_join_table
                WHERE project_fqid = NEW.project_fqid
                AND file_fqid=NEW.file_fqid
            )
            DO INSTEAD NOTHING;
        """
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP RULE IF EXISTS project_file_join_table_ignore_duplicate_inserts ON project_file_join_table;")
    op.execute("DROP RULE IF EXISTS project_table_ignore_duplicate_inserts ON projects_all_versions;")
    op.drop_index(op.f('ix_project_file_join_table_project_fqid'), table_name='project_file_join_table')
    op.drop_index(op.f('ix_project_file_join_table_file_fqid'), table_name='project_file_join_table')
    op.drop_table('project_file_join_table')
    op.drop_index(op.f('ix_projects_all_versions_version'), table_name='projects_all_versions')
    op.drop_index(op.f('ix_projects_all_versions_uuid'), table_name='projects_all_versions')
    op.drop_index(op.f('ix_projects_all_versions_fqid'), table_name='projects_all_versions')
    op.drop_table('projects_all_versions')

    # ### end Alembic commands ###
