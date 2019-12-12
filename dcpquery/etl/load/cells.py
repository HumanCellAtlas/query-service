import logging

import loompy as loompy

from dcpquery import config
from dcpquery.db.models.cell import Cell, Expression, Feature
from dcpquery.db.models.enums import ExpressionTypeEnum
from dcpquery.db.models.modules import Ontology, Accession

logger = logging.getLogger(__name__)


def handle_matrix(file_name):
    try:
        ds = loompy.connect(file_name)
        cells = create_cells(ds)  # 267360
        genes = create_genes(ds)  # 58347
        for (ix, selection, view) in ds.scan(axis=1):
            cell_start = ix
            gene_counter = 0
            mini_matrix = view
            while gene_counter < len(genes):
                gene_row = mini_matrix[gene_counter]
                feature_accession_id = genes[gene_counter]
                cell_counter = 0
                while cell_counter < len(gene_row):
                    cell_key = cells[cell_start + cell_counter]
                    if gene_row[cell_counter] > 0:
                        expression = get_or_create_expression(
                            expr_type=ExpressionTypeEnum('COUNT'),
                            expr_value=int(gene_row[cell_counter]),
                            cell_key=cell_key,
                            feature_accession_id=feature_accession_id
                        )
                        config.db_session.add(expression)
                    cell_counter += 1
                config.db_session.commit()
                gene_counter += 1
                if gene_counter % 10000 == 0:
                    print(f"Here we are {gene_counter}, {cell_key}")
    except Exception as e:
        print(e)
    finally:
        ds.close()


def create_cells(ds):
    i = 0
    cells = []
    while i < len(ds.ca.CellID):
        try:
            cell = get_or_create_cell(
                barcode=ds.ca['barcode'][i],
                key=ds.ca['CellID'][i],
                genes_detected=ds.ca['genes_detected'][i],
                total_umis=ds.ca['total_umis'][i],
                empty_drops_is_cell=ds.ca['emptydrops_is_cell'][i],
                sequence_file_uuid=ds.ca['file_uuid'][i],
                cell_suspension_uuid=ds.ca['cell_suspension.provenance.document_id'][i],
            )
            cells.append(cell.cellkey)
            if i % 1000 == 0:
                config.db_session.commit()
                print(f"Cells processed {i}")
        except Exception as e:
            print(e)
        i += 1

    return cells


def create_genes(ds):
    i = 0
    genes = []
    while i < len(ds.row_attrs.Gene):
        gene = get_or_create_feature(
            id=ds.ra['Gene'][i],
            accession=ds.ra['Accession'][i],
            type=ds.ra['featuretype'][i],
            name=ds.ra['Gene'][i],
            start=ds.ra['featurestart'][i],
            end=ds.ra['featureend'][i],
            chromosome=ds.ra['chromosome'][i],
            is_gene=ds.ra['isgene'][i],
            genus_species=ds.ra['genus_species'][i],
        )
        genes.append(gene.accession.id)
        if i % 1000 == 0:
            config.db_session.commit()
            print(f"genes created: {i}")
        i += 1
    return genes


def get_or_create_cell(barcode, key, genes_detected, total_umis, empty_drops_is_cell, sequence_file_uuid,
                       cell_suspension_uuid):
    if empty_drops_is_cell == 'f':
        empty_drops_is_cell = False
    if empty_drops_is_cell == 't':
        empty_drops_is_cell = True
    try:
        cell = Cell.get_or_create(
            cellkey=str(key),
            genes_detected=int(genes_detected),
            total_umis=float(total_umis),
            empty_drops_is_cell=empty_drops_is_cell,
            barcode=str(barcode),  # String in matrix service
            file_uuid=str(sequence_file_uuid), # todo add join table once matrices and metadata loaded in
            cell_suspension_uuid=str(cell_suspension_uuid),  # not sure if actually necessary bc can walk graph
            # bundle_uuid=bundle_uuid  # remove
        )
    except Exception as e:
        logger.info(f"Issue creating cell: {key} {e}")
    return cell


def get_or_create_expression(expr_type, expr_value, cell_key, feature_accession_id):
    expression = Expression.create(
        expr_type=expr_type,
        expr_value=int(expr_value),
        cell_key=str(cell_key),
        feature_accession_id=str(feature_accession_id)
    )
    return expression


def get_or_create_feature(id, accession, type, name, start, end, chromosome, is_gene, genus_species):
    ontology = Ontology.get_by_label(ontology_label=str(genus_species))
    accession = Accession.get_or_create(id=str(accession))
    if is_gene == 1:
        is_gene = True
    if is_gene == 0:
        is_gene = False
    feature = Feature.create(
        id=str(id),  # should this be unique?
        type=str(type),  # todo make an enum?
        name=str(name),
        feature_start=str(start),
        feature_end=str(end),
        chromosome=str(chromosome),
        is_gene=is_gene,
        genus_species=ontology,
        accession=accession
    )
    return feature
