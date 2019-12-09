"""Create Rules

Revision ID: 799eadf9234d
Revises: 71aea67e842a
Create Date: 2019-12-09 02:40:10.944907

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '799eadf9234d'
down_revision = '71aea67e842a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""

                    CREATE OR REPLACE RULE access_groups_ignore_duplicate_inserts AS
                        ON INSERT TO access_groups
                            WHERE EXISTS (
                                SELECT 1
                            FROM access_groups
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE accessions_ignore_duplicate_inserts AS
                        ON INSERT TO accessions
                            WHERE EXISTS (
                                SELECT 1
                            FROM accessions
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE annotations_ignore_duplicate_inserts AS
                        ON INSERT TO annotations
                            WHERE EXISTS (
                                SELECT 1
                            FROM annotations
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE barcodes_ignore_duplicate_inserts AS
                        ON INSERT TO barcodes
                            WHERE EXISTS (
                                SELECT 1
                            FROM barcodes
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE biomaterials_ignore_duplicate_inserts AS
                        ON INSERT TO biomaterials
                            WHERE EXISTS (
                                SELECT 1
                            FROM biomaterials
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE causes_of_death_ignore_duplicate_inserts AS
                        ON INSERT TO causes_of_death
                            WHERE EXISTS (
                                SELECT 1
                            FROM causes_of_death
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE familial_relationships_ignore_duplicate_inserts AS
                        ON INSERT TO familial_relationships
                            WHERE EXISTS (
                                SELECT 1
                            FROM familial_relationships
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE files_ignore_duplicate_inserts AS
                        ON INSERT TO files
                            WHERE EXISTS (
                                SELECT 1
                            FROM files
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE funders_ignore_duplicate_inserts AS
                        ON INSERT TO funders
                            WHERE EXISTS (
                                SELECT 1
                            FROM funders
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE growth_conditions_ignore_duplicate_inserts AS
                        ON INSERT TO growth_conditions
                            WHERE EXISTS (
                                SELECT 1
                            FROM growth_conditions
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    # op.execute("""
    #
    #                 CREATE OR REPLACE RULE links_ignore_duplicate_inserts AS
    #                     ON INSERT TO links
    #                         WHERE EXISTS (
    #                             SELECT 1
    #                         FROM links
    #                         WHERE uuid = NEW.uuid
    #                     )
    #                     DO INSTEAD NOTHING
    #                 """
    #            )
    op.execute("""

                    CREATE OR REPLACE RULE medical_histories_ignore_duplicate_inserts AS
                        ON INSERT TO medical_histories
                            WHERE EXISTS (
                                SELECT 1
                            FROM medical_histories
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE ontologies_ignore_duplicate_inserts AS
                        ON INSERT TO ontologies
                            WHERE EXISTS (
                                SELECT 1
                            FROM ontologies
                            WHERE ontology = NEW.ontology
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE parameters_ignore_duplicate_inserts AS
                        ON INSERT TO parameters
                            WHERE EXISTS (
                                SELECT 1
                            FROM parameters
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE plate_based_sequencing_ignore_duplicate_inserts AS
                        ON INSERT TO plate_based_sequencing
                            WHERE EXISTS (
                                SELECT 1
                            FROM plate_based_sequencing
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE projects_ignore_duplicate_inserts AS
                        ON INSERT TO projects
                            WHERE EXISTS (
                                SELECT 1
                            FROM projects
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE reagents_ignore_duplicate_inserts AS
                        ON INSERT TO reagents
                            WHERE EXISTS (
                                SELECT 1
                            FROM reagents
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE tasks_ignore_duplicate_inserts AS
                        ON INSERT TO tasks
                            WHERE EXISTS (
                                SELECT 1
                            FROM tasks
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE ten_x_ignore_duplicate_inserts AS
                        ON INSERT TO ten_x
                            WHERE EXISTS (
                                SELECT 1
                            FROM ten_x
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE users_ignore_duplicate_inserts AS
                        ON INSERT TO users
                            WHERE EXISTS (
                                SELECT 1
                            FROM users
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE biomaterial_accession_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO biomaterial_accession_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM biomaterial_accession_join_table
                            WHERE accession_uuid = NEW.accession_uuid
                            AND biomaterial_uuid = NEW.biomaterial_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE cell_morphologies_ignore_duplicate_inserts AS
                        ON INSERT TO cell_morphologies
                            WHERE EXISTS (
                                SELECT 1
                            FROM cell_morphologies
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE contributors_ignore_duplicate_inserts AS
                        ON INSERT TO contributors
                            WHERE EXISTS (
                                SELECT 1
                            FROM contributors
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE disease_ontologies_ignore_duplicate_inserts AS
                        ON INSERT TO disease_ontologies
                            WHERE EXISTS (
                                SELECT 1
                            FROM disease_ontologies
                            WHERE ontology = NEW.ontology
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE features_ignore_duplicate_inserts AS
                        ON INSERT TO features
                            WHERE EXISTS (
                                SELECT 1
                            FROM features
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE file_ontology_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO file_ontology_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM file_ontology_join_table
                            WHERE ontology_id = NEW.ontology_id
                            AND file_uuid = NEW.file_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE organoid_ignore_duplicate_inserts AS
                        ON INSERT TO organoid
                            WHERE EXISTS (
                                SELECT 1
                            FROM organoid
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE preservation_storage_ignore_duplicate_inserts AS
                        ON INSERT TO preservation_storage
                            WHERE EXISTS (
                                SELECT 1
                            FROM preservation_storage
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE processes_ignore_duplicate_inserts AS
                        ON INSERT TO processes
                            WHERE EXISTS (
                                SELECT 1
                            FROM processes
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE project_access_group_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO project_access_group_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM project_access_group_join_table
                            WHERE project_uuid = NEW.project_uuid
                            AND access_group_uuid = NEW.access_group_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE project_accession_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO project_accession_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM project_accession_join_table
                            WHERE project_uuid = NEW.project_uuid
                            AND accessions_uuid = NEW.accessions_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE project_funder_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO project_funder_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM project_funder_join_table
                            WHERE project_uuid = NEW.project_uuid
                            AND funder_uuid = NEW.funder_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE project_link_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO project_link_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM project_link_join_table
                            WHERE project_uuid = NEW.project_uuid
                            AND link_uuid = NEW.link_uuid                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE protocols_ignore_duplicate_inserts AS
                        ON INSERT TO protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE publications_ignore_duplicate_inserts AS
                        ON INSERT TO publications
                            WHERE EXISTS (
                                SELECT 1
                            FROM publications
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE sequence_files_ignore_duplicate_inserts AS
                        ON INSERT TO sequence_files
                            WHERE EXISTS (
                                SELECT 1
                            FROM sequence_files
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE time_courses_ignore_duplicate_inserts AS
                        ON INSERT TO time_courses
                            WHERE EXISTS (
                                SELECT 1
                            FROM time_courses
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE user_access_group_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO user_access_group_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM user_access_group_join_table
                            WHERE user_uuid = NEW.user_uuid
                            AND access_group_uuid = NEW.access_group_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE analysis_protocols_ignore_duplicate_inserts AS
                        ON INSERT TO analysis_protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM analysis_protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE cell_lines_ignore_duplicate_inserts AS
                        ON INSERT TO cell_lines
                            WHERE EXISTS (
                                SELECT 1
                            FROM cell_lines
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE cell_suspensions_ignore_duplicate_inserts AS
                        ON INSERT TO cell_suspensions
                            WHERE EXISTS (
                                SELECT 1
                            FROM cell_suspensions
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE collection_protocols_ignore_duplicate_inserts AS
                        ON INSERT TO collection_protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM collection_protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE differentiation_protocol_ignore_duplicate_inserts AS
                        ON INSERT TO differentiation_protocol
                            WHERE EXISTS (
                                SELECT 1
                            FROM differentiation_protocol
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE dissociation_protocols_ignore_duplicate_inserts AS
                        ON INSERT TO dissociation_protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM dissociation_protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE donor_organism_ignore_duplicate_inserts AS
                        ON INSERT TO donor_organism
                            WHERE EXISTS (
                                SELECT 1
                            FROM donor_organism
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE enrichment_protocols_ignore_duplicate_inserts AS
                        ON INSERT TO enrichment_protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM enrichment_protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE ipsc_induction_protocols_ignore_duplicate_inserts AS
                        ON INSERT TO ipsc_induction_protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM ipsc_induction_protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE library_prep_protocols_ignore_duplicate_inserts AS
                        ON INSERT TO library_prep_protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM library_prep_protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE process_biomaterial_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_biomaterial_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_biomaterial_join_table
                            WHERE process_uuid = NEW.process_uuid
                            AND connection_type=NEW.connection_type
                            AND biomaterial_uuid=NEW.biomaterial_uuid
                            AND project_uuid=NEW.project_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE process_file_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_file_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_file_join_table
                            WHERE process_uuid = NEW.process_uuid
                            AND connection_type=NEW.connection_type
                            AND file_uuid=NEW.file_uuid
                            AND project_uuid=NEW.project_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE process_parameter_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_parameter_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_parameter_join_table
                            WHERE process_uuid = NEW.process_uuid
                            AND parameter_uuid = NEW.parameter_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    # TODO drop
    op.execute("""

                    CREATE OR REPLACE RULE process_project_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_project_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_project_join_table
                            WHERE process_uuid = NEW.process_uuid
                            AND project_uuid = NEW.project_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE process_protocol_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_protocol_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_protocol_join_table
                            WHERE process_uuid = NEW.process_uuid
                            AND connection_type=NEW.connection_type
                            AND protocol_uuid=NEW.protocol_uuid
                            AND project_uuid=NEW.project_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE process_self_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_self_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_self_join_table
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE process_task_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_task_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_task_join_table
                            WHERE process_uuid = NEW.process_uuid
                            AND task_uuid = NEW.task_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE project_contributor_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO project_contributor_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM project_contributor_join_table
                            WHERE project_uuid = NEW.project_uuid
                            AND contributor_uuid = NEW.contributor_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE project_publication_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO project_publication_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM project_publication_join_table
                            WHERE project_uuid = NEW.project_uuid
                            AND publication_uuid = NEW.publication_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE protocol_reagent_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO protocol_reagent_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM protocol_reagent_join_table
                            WHERE protocol_uuid = NEW.protocol_uuid
                            AND reagent_uuid = NEW.reagent_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE sequence_file_accession_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO sequence_file_accession_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM sequence_file_accession_join_table
                            WHERE sequence_file_uuid = NEW.sequence_file_uuid
                            AND accession_uuid = NEW.accession_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE sequencing_protocols_ignore_duplicate_inserts AS
                        ON INSERT TO sequencing_protocols
                            WHERE EXISTS (
                                SELECT 1
                            FROM sequencing_protocols
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE specimens_ignore_duplicate_inserts AS
                        ON INSERT TO specimens
                            WHERE EXISTS (
                                SELECT 1
                            FROM specimens
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE cell_line_publication_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO cell_line_publication_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM cell_line_publication_join_table
                            WHERE cell_line_uuid = NEW.cell_line_uuid
                            AND publication_uuid = NEW.publication_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE cell_suspension_cell_type_ontology_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO cell_suspension_cell_type_ontology_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM cell_suspension_cell_type_ontology_join_table
                            WHERE cell_suspension_uuid = NEW.cell_suspension_uuid
                            AND cell_type_ontology_id = NEW.cell_type_ontology_id
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE cells_ignore_duplicate_inserts AS
                        ON INSERT TO cells
                            WHERE EXISTS (
                                SELECT 1
                            FROM cells
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE donor_organism_disease_ontology_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO donor_organism_disease_ontology_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM donor_organism_disease_ontology_join_table
                            WHERE donor_organism_uuid = NEW.donor_organism_uuid
                            AND disease_ontology_id = NEW.disease_ontology_id
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE specimen_disease_ontology_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO specimen_disease_ontology_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM specimen_disease_ontology_join_table
                            WHERE specimen_uuid = NEW.specimen_uuid
                            AND disease_ontology_id = NEW.disease_ontology_id
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE expressions_ignore_duplicate_inserts AS
                        ON INSERT TO expressions
                            WHERE EXISTS (
                                SELECT 1
                            FROM expressions
                            WHERE uuid = NEW.uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )
    op.execute("""

                    CREATE OR REPLACE RULE process_cell_join_table_ignore_duplicate_inserts AS
                        ON INSERT TO process_cell_join_table
                            WHERE EXISTS (
                                SELECT 1
                            FROM process_cell_join_table
                            WHERE process_uuid = NEW.process_uuid
                            AND connection_type=NEW.connection_type
                            AND cell_uuid=NEW.cell_uuid
                            AND project_uuid=NEW.project_uuid
                        )
                        DO INSTEAD NOTHING
                    """
               )


# create rule for ontologies to check ontology, accessions on type, id

def downgrade():
    table_list = ["access_groups",
                  "accessions",
                  "annotations",
                  "barcodes",
                  "biomaterials",
                  "causes_of_death",
                  "familial_relationships",
                  "files",
                  "funders",
                  "growth_conditions",
                  "links",
                  "medical_histories",
                  "ontologies",
                  "parameters",
                  "plate_based_sequencing",
                  "projects",
                  "reagents",
                  "tasks",
                  "ten_x",
                  "users",
                  "biomaterial_accession_join_table",
                  "cell_morphologies",
                  "contributors",
                  "disease_ontologies",
                  "features",
                  "file_ontology_join_table",
                  "organoid",
                  "preservation_storage",
                  "processes",
                  "project_access_group_join_table",
                  "project_accession_join_table",
                  "project_funder_join_table",
                  "project_link_join_table",
                  "protocols",
                  "publications",
                  "sequence_files",
                  "time_courses",
                  "user_access_group_join_table",
                  "analysis_protocols",
                  "cell_lines",
                  "cell_suspensions",
                  "collection_protocols",
                  "differentiation_protocol",
                  "dissociation_protocols",
                  "donor_organism",
                  "enrichment_protocols",
                  "ipsc_induction_protocols",
                  "library_prep_protocols",
                  "process_biomaterial_join_table",
                  "process_file_join_table",
                  "process_parameter_join_table",
                  "process_project_join_table",
                  "process_protocol_join_table",
                  "process_self_join_table",
                  "process_task_join_table",
                  "project_contributor_join_table",
                  "project_publication_join_table",
                  "protocol_reagent_join_table",
                  "sequence_file_accession_join_table",
                  "sequencing_protocols",
                  "specimens",
                  "cell_line_publication_join_table",
                  "cell_suspension_cell_type_ontology_join_table",
                  "cells",
                  "donor_organism_disease_ontology_join_table",
                  "specimen_disease_ontology_join_table",
                  "expressions",
                  "process_cell_join_table"]
    for table_name in table_list:
        op.execute(f"DROP RULE IF EXISTS {table_name}_ignore_duplicate_inserts ON {table_name};")
