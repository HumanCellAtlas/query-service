HCA DCP Query Service
=====================

# Introduction

The HCA DCP Query Service provides an interface for scientists and developers to query metadata associated with
experimental and analysis data stored in the [Human Cell Atlas](https://staging.data.humancellatlas.org/)
[Data Coordination Platform](https://www.humancellatlas.org/data-sharing) (DCP). Metadata from the
[DCP Data Store](https://github.com/HumanCellAtlas/data-store) are indexed and stored in an
[AWS Aurora](https://aws.amazon.com/rds/aurora/) [PostgreSQL](https://www.postgresql.org/) database.

Queries to the database can be sent over HTTP through the Query Service API
[Swagger Documentation](https://query.data.humancellatlas.org/v1/ui/#/)
or via the [Query Builder](https://query.data.humancellatlas.org/).

## Executing Queries
To execute a query via the swagger interface: 
- Click on the green `/query` row to expand it
- Click `Try it out`
- Edit the request body by adding in your query and any parameters. 

For example
```
{
  "params": {"s": 0},
  "query": "select * from files where size > %(s)s limit 10"
}
```
- click `Execute`

Note: Queries executed via the swagger interface can not contain new lines or tabs (you will need to edit some of the 
example queries by removing line breaks/tabs to make them work). These will generate a 400 error response 
containing the line `"detail": "Request body is not valid JSON"`. For complex queries that benefit from multi-line 
formatting we recommend using the [Query Builder](https://query.data.humancellatlas.org/). 
## Async Queries
For long-running queries (runtime over 20 seconds), the Query Service supports asynchronous tracking of query results.
When a long-running query triggers this mode, the caller will receive a
[`301 Moved Permanently`](https://en.wikipedia.org/wiki/HTTP_301) response status code with a `Retry-After` header. The caller
is expected to wait the specified amount of time before checking the redirect destination, or use the query job ID
returned in the response JSON body to check the status of the query job. The caller may turn off this functionality
(and cause the API to time out and return an error when a long-running query is encountered) by setting the
`async=False` flag when calling `/query`.

For large query results, the Query Service may deposit results in S3 instead of returning them verbatim in the response
body. In this case, the client will receive a [`302 Found`](https://en.wikipedia.org/wiki/HTTP_302) response status code
sending them to the response data location. In this mode, response data are confidential to the caller, and remain
accessible for 7 days. The caller may turn off this functionality by setting the `async=False` flag when calling
`/query`.

# Data Schema
![](QueryServiceDataSchema.svg)

Because there are often multiple, slightly different versions of a bundle or file, the `bundles_all_versions` and
`files_all_versions` tables contain all versions of the bundles and files. There are also derived view tables `files` 
and `bundles`, which only contain the latest version of each bundle or file. 

The metadata itself is available in `files.body` as a JSON data object. The structure of that document is dependent on 
the `dcp_schema_type_name` column. The schemas for each schema type can be found [here](https://schema.humancellatlas.org/a). 
It is also possible to pull the full JSON document for a file of a particular schema type (or the `aggregate_metadata` field 
for a bundle to see the combined metadata of multiple files) and explore it in your text editor to better understand 
what data it contains and how it is formatted.
For example, to get the JSON associated with a cell line
```postgresql
SELECT body FROM files WHERE dcp_schema_type='cell_line';
``` 
or
```postgresql
SELECT body FROM cell_line;
```
To simplify queries, the view tables for each schema type contain only the most recent version of each metadata file as 
the schema of the metadata may change between versions. 

Possible schema_types include 
`cell_line`,
`cell_suspension`,
`differentiation_protocol`,
`dissociation_protocol`,
`donor_organism`,
`ipsc_induction_protocol`,
`library_preparation_protocol`,
`links`,
`organoid`,
`process`,
`project`,
`sequence_file`,
`sequencing_protocol`,
`specimen_from_organism`,
`supplementary_file`,
`analysis_file`,
`analysis_process`,
`analysis_protocol`,
`collection_protocol`,
`enrichment_protocol`,
`biomaterial`,
`file`,
`image_file`,
`imaged_specimen`,
`imaging_preparation_protocol`,
`imaging_protocol`.


# Example Queries
Get a list of all of the tables:
```postgresql
SELECT table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
 AND table_schema NOT IN ('pg_catalog', 'information_schema')
 AND table_schema = 'public';
```
Get total number of bundles:
```postgresql
SELECT count(*) from bundles;
```
Get all data for 10 bundles:
```postgresql
SELECT * FROM bundles LIMIT 10;
```
Select the data for a particular bundle:

```postgresql
SELECT * FROM bundles WHERE uuid='cf48f5bc-7f20-4aa8-a0b6-6f889466546d'
```
If you query on `uuid` the database may return multiple versions of the bundle; to only get one, use the `fqid` (which is the `version` concatenated to the `uuid`)

## Querying the metadata body
The metadata itself is stored in the jsonb format. For help with the syntax of querying jsonb check out this [cheat sheet](https://hackernoon.com/how-to-query-jsonb-beginner-sheet-cheat-4da3aa5082a3).

Get a list of submissions for a particular submitter:
```postgresql
SELECT p.uuid, p.body->'project_core'->>'project_title' AS title
FROM project AS p
WHERE p.body @> '{"contributors": [{"contact_name": "Aviv,,Regev"}]}'
   OR p.body @> '{"contributors": [{"contact_name": "Sarah,,Teichmann"}]}';
```

## Querying the experimental graph
Experiments are represented in HCA's metadata as a [directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph) (DAG). Material entities--either `Project`, `File`, `Biomaterial`--are linked by immaterial entities--`Process` edges that implement a `Protocol`. For more see [this documentation](https://github.com/HumanCellAtlas/metadata-schema/blob/master/docs/structure.md#structure-overview).

### Traversing the graph of material entities

Using the `children_of_file` and `parents_of_file` postgres methods, you can find the child nodes and parent nodes of a given material entity in the experimental DAG respectively.

Let's say you have a FASTQ file and you are curious about the donor organism from which it was derived. If `6eeadcee-dd1a-4153-97db-db5778e830d7` is the UUID of a donor file, you can run:

```sql
SELECT parents_of_file('b7ae6dcb-b8fd-48d0-a7c7-252f8089c865');
```

The results are the uuids of files represent parent material entities in the DAG for this sequence file. In other words, `parents_of_file` returns all of the inputs that went into making the file with the given UUID.

If we want to get the donor organism from which this file was derived from, we simply join with the files table and filter:

```sql
SELECT * FROM files
WHERE
  uuid IN (SELECT parents_of_file('b7ae6dcb-b8fd-48d0-a7c7-252f8089c865')) AND
  dcp_schema_type_name = 'donor_organism';
```

Conversely, you could use the UUID of the donor organism to find the sequencing files derived from it:

```sql
SELECT * FROM files
WHERE
  uuid IN (SELECT children_of_file('2107cab5-4f14-4008-bc82-4df8637c05a9')) AND
  dcp_schema_type_name = 'sequence_file';
```
