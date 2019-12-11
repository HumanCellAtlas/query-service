import logging

import loompy as loompy

from dcpquery import config
from dcpquery.db.models.biomaterial import CellSuspension
from dcpquery.db.models.cell import Cell, Expression, Feature
from dcpquery.db.models.data_file import SequenceFile
from dcpquery.db.models.enums import ExpressionTypeEnum
from dcpquery.db.models.modules import Barcode, Ontology, Accession
from dcpquery.etl.load.modules import get_or_create_barcode

logger = logging.getLogger(__name__)

import loompy


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
                gene = genes[gene_counter]
                gene_row = mini_matrix[gene_counter]
                cell_counter = 0
                while cell_counter < len(gene_row):
                    cell = cells[cell_start + cell_counter]
                    if gene_row[cell_counter] > 0:
                        expression = get_or_create_expression(
                            expr_type=ExpressionTypeEnum('COUNT'),
                            expr_value=gene_row[cell_counter],
                            cell=cell,
                            feature=gene
                        )
                        config.db_session.add(expression)
                    cell_counter += 1
                config.db_session.commit()
                gene_counter += 1
                if gene_counter % 100 == 0:
                    print(f"Here we are {cell_start}, {gene_counter}")

    except Exception as e:
        print(e)
        import pdb
        pdb.set_trace()
    finally:
        ds.close()


def create_cells(ds):
    i = 0
    cells = []
    while i < len(ds.ca.CellID):
        cell = get_or_create_cell(
            barcode_string=ds.ca['barcode'][i],
            key=ds.ca['CellID'][i],
            genes_detected=ds.ca['genes_detected'][i],
            total_umis=ds.ca['total_umis'][i],
            empty_drops_is_cell=ds.ca['emptydrops_is_cell'][i],
            sequence_file_uuid=ds.ca['file_uuid'][i],
            cell_suspension_uuid=ds.ca['cell_suspension.provenance.document_id'][i],
        )
        cell.append(cell)
        if i % 1000 == 0:
            config.db_session.commit()
            print(i)
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
            genus_species=ds.ra.genus_species[i],
        )
        genes.append(gene)
        if i % 1000 == 0:
            config.db_session.commit()
            print(i)
        i += 1
    return genes


def get_or_create_cell(barcode_string, key, genes_detected, total_umis, empty_drops_is_cell, sequence_file_uuid,
                       cell_suspension_uuid):
    barcode = Barcode.get_or_create_by_string(barcode_string=barcode_string)
    if empty_drops_is_cell == 'f':
        empty_drops_is_cell = False
    if empty_drops_is_cell == 't':
        empty_drops_is_cell = True
    cell_suspension = CellSuspension.get_or_create(uuid=cell_suspension_uuid)
    sequence_file = SequenceFile.get_or_create(uuid=sequence_file_uuid)

    cell = Cell.get_or_create(
        cellkey=key,
        genes_detected=genes_detected,
        total_umis=total_umis,
        empty_drops_is_cell=empty_drops_is_cell,
        barcode=barcode,  # String in matrix service?
        file=sequence_file,
        cell_suspension=cell_suspension,  # not sure if actually necessary bc can walk graph
        # bundle_uuid=bundle_uuid  # remove
    )
    return cell


def get_or_create_expression(expr_type, expr_value, cell, feature):
    expression = Expression.get_or_create(
        expr_type=expr_type,  # todo make an enmu?
        expr_value=expr_value,
        cell=cell,
        feature=feature
    )
    return expression


def get_or_create_feature(id, accession, type, name, start, end, chromosome, is_gene, genus_species):
    ontology = Ontology.get_by_label(ontology_label=genus_species)
    accession = Accession.get_or_create(id=accession)
    if is_gene == 1:
        is_gene = True
    if is_gene == 0:
        is_gene = False
    feature = Feature.create(
        id=id,  # should this be unique?
        accession=accession,
        type=type,  # todo make an enum?
        name=name,
        feature_start=start,
        feature_end=end,
        chromosome=chromosome,
        is_gene=is_gene,
        genus_species=ontology,
    )

    return feature
