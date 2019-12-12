import http
import json

from dcplib.networking import HTTPRequest

from dcpquery.etl.output import bundle_uuids


def extract_bundles(bundle_uuids):
    query_url = "https://query.data.humancellatlas.org/v1/query"
    http = HTTPRequest()
    headers = {'accept': '*/*', 'Content-Type': 'application/json'}
    query = f"SELECT aggregate_metadata FROM bundles where uuid in {tuple(bundle_uuids)};"
    response = http.post(query_url,
                         data=json.dumps({"query": query}), headers=headers)
    return response.json()


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]
