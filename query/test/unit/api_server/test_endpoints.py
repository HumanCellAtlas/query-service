import datetime
import json
import os
import psycopg2
import sys
import unittest

from unittest.mock import patch
from test import *

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from query.test.unit.api_server import client_for_test_api_server


class TestEndpoints(unittest.TestCase):

    def test_heathcheck_endpoint(self):
        self.client = client_for_test_api_server()

        response = self.client.get(f"/v1/health")
        self.assertEqual(response.status_code, 200)

    @patch('query.lambdas.api_server.v1.fast_query.db.run_read_only_query')
    def test_query_endpoint(self, mock_ro_query):
        self.maxDiff = None

        query_result = [
            (
                '803fd65a-c578-4c4f-a39e-bedec24e2578',
                '2018, 10, 11, 21, 18, 13, 146000',
                '803fd65a-c578-4c4f-a39e-bedec24e2578.2018-10-11T211813.146000Z',
                'cell_suspension_0.json',
                2,
                {
                    'provenance': {
                         'document_id': '803fd65a-c578-4c4f-a39e-bedec24e2578',
                        'update_date': '2018-10-11T21:18:13.146Z',
                        'submission_date': '2018-10-11T21:18:02.832Z'
                    },
                     'describedBy': 'http://schema.staging.data.humancellatlas.org/type/biomaterial/8.6.1/cell_suspension',
                     'schema_type': 'biomaterial',
                     'genus_species': [
                         {
                             'text': 'Homo sapiens',
                             'ontology': 'NCBITaxon:9606'
                         }],
                     'biomaterial_core': {
                         'ncbi_taxon_id': [9606],
                         'biomaterial_id': 'HPSI_organoids_pooled_2',
                         'biomaterial_name': 'pooled cells from 4 dissociated organoids',
                         'biomaterial_description': 'pooled cells from 4 dissociated organoids (wibj_2, kucg_2, hoik_1, sojd_3)'
                     },
                     'selected_cell_type': [
                         {
                             'text': 'neural cell',
                             'ontology': 'CL:0002319'
                         }],
                     'total_estimated_cells': 6210
                }
            ),
            (
                '2d8282f0-6cbb-4d5a-822c-4b01718b4d0d',
                '2018, 10, 11, 21, 18, 13, 146000',
                '2d8282f0-6cbb-4d5a-822c-4b01718b4d0d.2018-10-11T211812.864000Z',
                'organoid_0.json',
                3,
                {
                    'provenance': {
                        'document_id': '2d8282f0-6cbb-4d5a-822c-4b01718b4d0d',
                        'update_date': '2018-10-11T21:18:12.864Z',
                        'submission_date': '2018-10-11T21:18:02.654Z'
                    },
                    'describedBy': 'http://schema.staging.data.humancellatlas.org/type/biomaterial/8.3.8/organoid',
                    'schema_type': 'biomaterial',
                    'organoid_age': 62,
                    'genus_species': [
                        {
                            'text': 'Homo sapiens',
                            'ontology': 'NCBITaxon:9606'
                        }
                    ],
                    'organoid_type': 'stem cell-derived',
                    'model_for_organ': {
                        'text': 'Brain',
                        'ontology': 'UBERON:0000955'
                    },
                    'biomaterial_core': {
                        'ncbi_taxon_id': [9606],
                        'biomaterial_id': 'Org_HPSI0214i-wibj_2_2',
                        'biomaterial_name': 'human cerebral organoid wibj_2',
                        'biomaterial_description': 'human cerebral organoid wibj_2, 62d'
                    },
                    'organoid_age_unit': {
                        'text': 'day',
                        'ontology': 'UO:0000033'
                    },
                    'embedded_in_matrigel': True,
                    'organoid_growth_environment': 'suspension'
                }
            ),
            (
                'b7214641-1ac5-4f60-b795-cb33a7c25434',
                '2018, 10, 11, 21, 18, 13, 146000',
                'b7214641-1ac5-4f60-b795-cb33a7c25434.2018-10-11T211812.763000Z',
                'organoid_1.json',
                3,
                {
                    'provenance': {
                        'document_id': 'b7214641-1ac5-4f60-b795-cb33a7c25434',
                        'update_date': '2018-10-11T21:18:12.763Z',
                        'submission_date': '2018-10-11T21:18:02.696Z'
                    },
                    'describedBy': 'http://schema.staging.data.humancellatlas.org/type/biomaterial/8.3.8/organoid',
                    'schema_type': 'biomaterial',
                    'organoid_age': 62,
                    'genus_species': [
                        {
                            'text': 'Homo sapiens',
                            'ontology': 'NCBITaxon:9606'
                        }
                    ],
                    'organoid_type': 'stem cell-derived',
                    'model_for_organ': {
                        'text': 'Brain',
                        'ontology': 'UBERON:0000955'
                    },
                    'biomaterial_core': {
                        'ncbi_taxon_id': [9606],
                        'biomaterial_id': 'Org_HPSI0214i-kucg_2_2',
                        'biomaterial_name': 'human cerebral organoid kucg_2',
                        'biomaterial_description': 'human cerebral organoid kucg_2, 62d'
                    },
                    'organoid_age_unit': {
                        'text': 'day',
                        'ontology': 'UO:0000033'
                    },
                    'embedded_in_matrigel': True,
                    'organoid_growth_environment': 'suspension'}
            )
        ]
        column_names = ['uuid', 'version', 'fqid', 'name', 'schema_type_id', 'json']
        expected_results = [
            {
                'fqid': '803fd65a-c578-4c4f-a39e-bedec24e2578.2018-10-11T211813.146000Z',
                'json': {
                    'biomaterial_core': {
                        'biomaterial_description': 'pooled cells from 4 dissociated organoids (wibj_2, kucg_2, hoik_1, sojd_3)',
                        'biomaterial_id': 'HPSI_organoids_pooled_2',
                        'biomaterial_name': 'pooled cells from 4 dissociated organoids',
                        'ncbi_taxon_id': [9606]
                    },
                    'describedBy': 'http://schema.staging.data.humancellatlas.org/type/biomaterial/8.6.1/cell_suspension',
                    'genus_species': [
                        {'ontology': 'NCBITaxon:9606',
                         'text': 'Homo sapiens'
                         }
                    ],
                    'provenance': {
                        'document_id': '803fd65a-c578-4c4f-a39e-bedec24e2578',
                        'submission_date': '2018-10-11T21:18:02.832Z',
                        'update_date': '2018-10-11T21:18:13.146Z'
                    },
                    'schema_type': 'biomaterial',
                    'selected_cell_type': [{'ontology': 'CL:0002319',
                                            'text': 'neural cell'}],
                    'total_estimated_cells': 6210},
                'name': 'cell_suspension_0.json',
                'schema_type_id': 2,
                'uuid': '803fd65a-c578-4c4f-a39e-bedec24e2578',
                'version': '2018, 10, 11, 21, 18, 13, 146000'
            },
            {'fqid': '2d8282f0-6cbb-4d5a-822c-4b01718b4d0d.2018-10-11T211812.864000Z',
             'json': {'biomaterial_core': {'biomaterial_description': 'human cerebral '
                                                                      'organoid wibj_2, '
                                                                      '62d',
                                           'biomaterial_id': 'Org_HPSI0214i-wibj_2_2',
                                           'biomaterial_name': 'human cerebral organoid '
                                                               'wibj_2',
                                           'ncbi_taxon_id': [9606]},
                      'describedBy': 'http://schema.staging.data.humancellatlas.org/type/biomaterial/8.3.8/organoid',
                      'embedded_in_matrigel': True,
                      'genus_species': [{'ontology': 'NCBITaxon:9606',
                                         'text': 'Homo sapiens'}],
                      'model_for_organ': {'ontology': 'UBERON:0000955', 'text': 'Brain'},
                      'organoid_age': 62,
                      'organoid_age_unit': {'ontology': 'UO:0000033', 'text': 'day'},
                      'organoid_growth_environment': 'suspension',
                      'organoid_type': 'stem cell-derived',
                      'provenance': {'document_id': '2d8282f0-6cbb-4d5a-822c-4b01718b4d0d',
                                     'submission_date': '2018-10-11T21:18:02.654Z',
                                     'update_date': '2018-10-11T21:18:12.864Z'},
                      'schema_type': 'biomaterial'},
             'name': 'organoid_0.json',
             'schema_type_id': 3,
             'uuid': '2d8282f0-6cbb-4d5a-822c-4b01718b4d0d',
             'version': '2018, 10, 11, 21, 18, 13, 146000'
             },
            {'fqid': 'b7214641-1ac5-4f60-b795-cb33a7c25434.2018-10-11T211812.763000Z',
             'json': {'biomaterial_core': {'biomaterial_description': 'human cerebral '
                                                                      'organoid kucg_2, '
                                                                      '62d',
                                           'biomaterial_id': 'Org_HPSI0214i-kucg_2_2',
                                           'biomaterial_name': 'human cerebral organoid '
                                                               'kucg_2',
                                           'ncbi_taxon_id': [9606]},
                      'describedBy': 'http://schema.staging.data.humancellatlas.org/type/biomaterial/8.3.8/organoid',
                      'embedded_in_matrigel': True,
                      'genus_species': [{'ontology': 'NCBITaxon:9606',
                                         'text': 'Homo sapiens'}],
                      'model_for_organ': {'ontology': 'UBERON:0000955', 'text': 'Brain'},
                      'organoid_age': 62,
                      'organoid_age_unit': {'ontology': 'UO:0000033', 'text': 'day'},
                      'organoid_growth_environment': 'suspension',
                      'organoid_type': 'stem cell-derived',
                      'provenance': {'document_id': 'b7214641-1ac5-4f60-b795-cb33a7c25434',
                                     'submission_date': '2018-10-11T21:18:02.696Z',
                                     'update_date': '2018-10-11T21:18:12.763Z'},
                      'schema_type': 'biomaterial'},
             'name': 'organoid_1.json',
             'schema_type_id': 3,
             'uuid': 'b7214641-1ac5-4f60-b795-cb33a7c25434',
             'version': '2018, 10, 11, 21, 18, 13, 146000'}]
        mock_ro_query.return_value = query_result, column_names
        self.client = client_for_test_api_server()
        query = "Select * From files;"
        response = self.client.post(f"/v1/query", data=json.dumps(query))
        self.assertEqual(response.status_code, 200)

        expected_response_data = {"query": query, "results": expected_results}
        self.assertEqual(json.loads(response.data), expected_response_data)
