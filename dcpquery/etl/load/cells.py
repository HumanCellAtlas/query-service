import concurrent
import logging

import loompy as loompy

from dcpquery import config
from dcpquery.db.models.cell import Cell, Expression, Feature
from dcpquery.db.models.enums import ExpressionTypeEnum
from dcpquery.db.models.modules import Ontology, Accession

logger = logging.getLogger(__name__)


def handle_matrices():
    file_urls = [
        'https://data.humancellatlas.org/project-assets/project-matrices/4a95101c-9ffc-4f30-a809-f04518a23803.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/8185730f-4113-40d3-9cc3-929271784c2b.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/005d611a-14d5-4fbf-846e-571a1f874f70.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/cc95ff89-2e68-4a08-a234-480eca21ce79.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/4d6f6c96-2a83-43d8-8fe1-0f53bffd4674.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/c4077b3c-5c98-4d26-a614-246d12c2e5d7.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/091cf39b-01bc-42e5-9437-f419a66c8a45.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/f83165c5-e2ea-4d15-a5cf-33f3550bffde.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/f8aa201c-4ff1-45a4-890e-840d63459ca2.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/abe1a013-af7a-45ed-8c26-f3793c24a1f4.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/2043c65a-1cf8-4828-a656-9e247d4e64f1.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/cddab57b-6868-4be4-806f-395ed9dd635a.homo_sapiens.loom',  # noqa
        'https://data.humancellatlas.org/project-assets/project-matrices/116965f3-f094-4769-9d28-ae675c1b569c.homo_sapiens.loom'  # noqa
    ]
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = {}
        for url in file_urls:
            matrix_uuid = '2043c65a-1cf8-4828-a656-9e247d4e64f1'

    print(file_urls)


def handle_matrix(file_url, matrix_uuid):
    file_url = 'https://data.humancellatlas.org/project-assets/project-matrices/abe1a013-af7a-45ed-8c26-f3793c24a1f4.homo_sapiens.loom'  # noqa
    matrix_uuid = 'abe1a013-af7a-45ed-8c26-f3793c24a1f4'
    try:
        get_loom_file(file_url, matrix_uuid)
        ds = loompy.connect(f'{matrix_uuid}.loom')
        read_loom_file(ds)
    except Exception as e:
        print(e)
    finally:
        ds.close()
        import os
        os.remove(f"{matrix_uuid}.loom")


def get_loom_file(file_url, bundle_uuid):
    from urllib.request import urlretrieve
    dst = f"{bundle_uuid}.loom"
    urlretrieve(file_url, dst)


def read_loom_file(ds):
    try:
        # ds = loompy.connect(file_name)
        cells = ds.ca.CellID  # 267360
        genes = ds.row_attrs.Gene  # 58347
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
                    logger.info(f"Here we are {gene_counter}, {cell_key}")
    except Exception as e:
        logger.info(e)
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
                logger.info(f"Cells processed {i}")
        except Exception as e:
            logger.info(e)
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
            logger.info(f"genes created: {i}")
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
            file_uuid=str(sequence_file_uuid),  # todo add join table once matrices and metadata loaded in
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
        genus_species_id_=str(genus_species),
        accession_id=str(accession)
    )
    return feature
