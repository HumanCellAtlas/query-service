#!/usr/bin/env python3
import json
import sys

from hca import HCAConfig
from hca.dss import DSSClient

"""
query_project.py

@input line separated project uuids from stdin
@output bundle FQIDs contained in that project
"""

hca_config = HCAConfig()
# TODO: lock to same environment as specified in DEPLOYMENT_STAGE
#from lib.config import Config
#hca_config['DSSClient'].swagger_url = f"https://dss.{Config.deployment_stage}.data.humancellatlas.org/v1/swagger.json"
hca_config['DSSClient'].swagger_url = f"https://dss.staging.data.humancellatlas.org/v1/swagger.json"
dss = DSSClient(config=hca_config)

if __name__ == '__main__':

    project_uuids = []
    for line in sys.stdin:
        project_uuid = line.strip()
        project_uuids.append(project_uuid)

    for project_uuid in project_uuids:
        results = dss.post_search.iterate(
            replica='aws',
            es_query={
                "query": {
                    "match": {
                        "files.project_json.provenance.document_id": project_uuid
                    }
                }
            }
        )
        f = open('fqids.txt', 'w+')
        for r in results:
            f.write(r['bundle_fqid']+"\n")
        f.close()
