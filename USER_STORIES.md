# User Stories and Matching Queries

Query user stories taken from the [Blue Box Queries
Table](https://docs.google.com/spreadsheets/d/1PBMrc0oql4gPpH_cQMqlf7ASNMwePRQZNCutxeSFze8/edit#gid=0)

## 1
Please give me a list of all the contact emails and titles for all the projects, and how many samples (specimens) and sequencing files each project has.

### emails
```sql
SELECT p.json->'project_core'->>'project_title' AS title, jsonb_agg(contributors->'email') AS emails
FROM projects AS p,
     jsonb_array_elements(p.json->'contributors') AS contributors
GROUP BY 1;
```

### specimen count per project
```sql
SELECT p.uuid                                   AS project_uuid,
       p.json->'project_core'->>'project_title' AS project_title,
       s.json->'organ'->>'text'                 AS organ,
       count(DISTINCT(s.uuid))                  AS specimen_count
FROM bundles AS b
       JOIN specimen_from_organisms AS s ON s.fqid = ANY(b.file_fqids)
       JOIN projects AS p ON p.fqid = ANY(b.file_fqids)
GROUP BY 1, 2, 3;
```

### data (sequence) file count per project

Array variant (runtime@[19938 bundles, 411394 files]: 11s 638ms)

```sql
SELECT p.uuid                                   AS project_uuid,
       p.json->'project_core'->>'project_title' AS project_title,
       count(DISTINCT(f.uuid))                  AS file_count
FROM bundles AS b
       JOIN files AS f ON f.fqid = ANY(b.file_fqids)
       JOIN projects AS p ON p.fqid = ANY(b.file_fqids)
       JOIN schema_types st ON f.schema_type_id = st.id
WHERE st.name = 'sequence_file'
GROUP BY 1, 2;
```

Join table variant (runtime 17s 708ms)

```sql
WITH bundles_specimens AS (SELECT b.uuid AS bundle_uuid, s.uuid AS file_uuid, s.json->'organ'->>'text' AS organ
                           FROM bundles AS b
                                  JOIN bundles_files AS bf
                                    ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
                                  JOIN specimen_from_organisms AS s
                                    ON (bf.file_uuid = s.uuid AND bf.file_version = s.version)),
     bundles_projects AS (SELECT b.uuid                                   AS bundle_uuid,
                                 p.uuid                                   AS project_uuid,
                                 p.json->'project_core'->>'project_title' AS project_title
                          FROM bundles AS b
                                 JOIN bundles_files AS bf ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
                                 JOIN projects AS p ON (bf.file_uuid = p.uuid AND bf.file_version = p.version))
SELECT bp.project_uuid, bp.project_title, bs.organ, count(DISTINCT bs.file_uuid)
FROM bundles_specimens AS bs,
     bundles_projects AS bp
WHERE bs.bundle_uuid = bp.bundle_uuid
GROUP BY 1, 2, 3;
```

## 2
I’m trying to figure out whether this is a batch effect. Please try to find me examples where the same type of cell was sequenced by the same lab by two different single cell isolation and sequencing techniques. Please also find examples where the same type of cell was sequenced by two different labs using what is supposed to be the same technique.

## 3
Find all bundles specified in release 'X' with tissue type 'Y' Note: could substitute wide variety of other bio constraint, eg, "with coverage gt 10X", etc.

```sql
/* can't do this without establishing release design first */
```

## 4
Find all fastq single cell files that are from a human, that hasn't been processed (no analysis.json file)

Array variant 1 (runtime@[19938 bundles, 411394 files]: 839ms, 2m 1s 250ms with `SELECT DISTICT ...`)

```sql
SELECT f.fqid, f.name
FROM bundles AS b
       LEFT JOIN analysis_files AS a ON a.fqid = ANY(b.file_fqids)
       JOIN donor_organisms AS d ON d.fqid = ANY(b.file_fqids)
       JOIN sequencing_protocols AS s ON s.fqid = ANY(b.file_fqids)
       JOIN files AS f ON f.fqid = ANY(b.file_fqids)
WHERE s.json @> '{"sequencing_approach": {"text": "RNA-Seq"}}'
  AND d.json @> '{"genus_species": [{"text": "Homo sapiens"}]}'
  AND f.name LIKE '%.fastq.gz';
```

Array variant 2 (runtime@[19938 bundles, 411394 files]: 11s 475ms)

```sql
SELECT *
FROM (SELECT f.fqid, f.name
      FROM bundles AS b
             JOIN donor_organisms AS d ON d.fqid = ANY(b.file_fqids)
             JOIN sequencing_protocols AS s ON s.fqid = ANY(b.file_fqids)
             JOIN files AS f ON f.fqid = ANY(b.file_fqids)
      WHERE s.json @> '{"sequencing_approach": {"text": "RNA-Seq"}}'
        AND d.json @> '{"genus_species": [{"text": "Homo sapiens"}]}'
      GROUP BY 1, 2
      HAVING 'analysis_0.json' != ANY(array_agg(f.name))) AS unanalyzed
WHERE name LIKE '%.fastq.gz';
```

Hybrid array and join table variant (runtime@[19938 bundles, 411394 files]: 9s 534ms)

```sql
WITH matching_bundles AS (SELECT DISTINCT b.uuid, b.version
                          FROM bundles AS b
                                 JOIN donor_organisms AS d ON d.fqid = ANY(b.file_fqids)
                                 JOIN sequencing_protocols AS s ON s.fqid = ANY(b.file_fqids)
                          WHERE s.json @> '{"sequencing_approach": {"text": "RNA-Seq"}}'
                            AND d.json @> '{"genus_species": [{"text": "Homo sapiens"}]}'),
     analyzed_bundles AS (SELECT DISTINCT b.uuid AS uuid
                          FROM bundles AS b
                                 JOIN bundles_files AS bf ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
                                 JOIN analysis_files AS a ON (bf.file_uuid = a.uuid AND bf.file_version = a.version))
SELECT f.fqid, f.name
FROM matching_bundles AS b
       LEFT JOIN analyzed_bundles AS a ON (b.uuid = a.uuid)
       JOIN bundles_files AS bf ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
       JOIN files AS f ON (bf.file_uuid = f.uuid AND bf.file_version = f.version)
WHERE f.name LIKE '%.fastq.gz';
```

Join table variant (runtime@[19938 bundles, 411394 files]: 1s 859ms)

```sql
WITH bundles_donors AS (SELECT DISTINCT b.uuid    AS bundle_uuid,
                                        b.version AS bundle_version,
                                        d.fqid    AS file_fqid,
                                        d.name    AS file_name
                        FROM bundles AS b
                               JOIN bundles_files AS bf ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
                               JOIN donor_organisms AS d ON (bf.file_uuid = d.uuid AND bf.file_version = d.version)
                        WHERE d.json @> '{"genus_species": [{"text": "Homo sapiens"}]}'),
     bundles_protocols AS (SELECT DISTINCT b.uuid    AS bundle_uuid,
                                           b.version AS bundle_version,
                                           s.fqid    AS file_fqid,
                                           s.name    AS file_name
                           FROM bundles AS b
                                  JOIN bundles_files AS bf
                                    ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
                                  JOIN sequencing_protocols AS s
                                    ON (bf.file_uuid = s.uuid AND bf.file_version = s.version)
                           WHERE s.json @> '{"sequencing_approach": {"text": "RNA-Seq"}}'),
     analyzed_bundles AS (SELECT DISTINCT b.uuid AS uuid
                          FROM bundles AS b
                                 JOIN bundles_files AS bf ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
                                 JOIN analysis_files AS a ON (bf.file_uuid = a.uuid AND bf.file_version = a.version))
SELECT DISTINCT f.fqid, f.name
FROM bundles AS b
       LEFT JOIN analyzed_bundles AS ab ON (b.uuid = ab.uuid)
       JOIN bundles_donors AS bd ON (b.uuid = bd.bundle_uuid AND b.version = bd.bundle_version)
       JOIN bundles_protocols AS bp ON (b.uuid = bp.bundle_uuid AND b.version = bp.bundle_version)
       JOIN bundles_files AS bf ON (b.uuid = bf.bundle_uuid AND b.version = bf.bundle_version)
       JOIN files AS f ON (bf.file_uuid = f.uuid AND bf.file_version = f.version)
WHERE f.name LIKE '%.fastq.gz';
```

## 5
What are all the files that were submitted as part of a project? (What are my submissions x timeframe, project name, new study) UI: should be able to page/facet for large lists. Would also like to see the status of each file that is retreived b y the query (may need to break this out into a separate case)

```sql
SELECT p.uuid AS project_uuid, f.uuid AS file_uuid, f.name AS filename
FROM bundles AS b
       JOIN projects AS p ON p.fqid = ANY(b.file_fqids)
       JOIN files AS f ON f.fqid = ANY(b.file_fqids)
       JOIN schema_types st ON f.schema_type_id = st.id
WHERE st.name IS NULL /* not a metadata file */
GROUP BY 1, 2, 3;
```

## 6 & 7
* What are all the files that are the results of analysis of files submitted as part of a project? (overlap with #5 above) Release bundles? “Terminal” or latest bundle
* find all bundles created with a specific method or reference (may want to reprocess the input bundles) May be a 2 step search, 1. Find all results created with a specific version/reference, 2. Use them to find all the source bundles

```sql
SELECT outputs.inputs, outputs.uuid AS output_uuid, outputs.process_uuid, f.fqid, f.name, f.json
FROM files AS f
       JOIN (SELECT links->'inputs'                                     AS inputs,
                    links->>'process'                                   AS process_uuid,
                    jsonb_array_elements_text(links->'outputs') :: UUID AS uuid
             FROM bundles AS b
                    JOIN projects p ON p.fqid = ANY(b.file_fqids)
                    JOIN links AS l ON l.fqid = ANY(b.file_fqids),
                  jsonb_array_elements(l.json->'links') AS links
             WHERE l.json @> '{"links": [{"protocols": [{"protocol_type": "sequencing_protocol"}]}]}'
               AND p.uuid = '08e7b6ba-5825-47e9-be2d-7978533c5f8c') AS outputs ON f.uuid = outputs.uuid;
```

## 8
What are all of the files of a particular format associated with an particular organ?

```sql
SELECT f.fqid, f.name
FROM bundles AS b
       JOIN files AS f ON f.fqid = ANY(b.file_fqids)
       JOIN specimen_from_organisms AS s ON s.fqid = ANY(b.file_fqids)
WHERE s.json @> '{"organ": {"text": "pancreas"}}'
  AND f.name LIKE '%.fastq.gz'
```

## 9
Here's a list of files I'm interested in. What is their total size? Count might also be useful

* TODO: depends on adding file size to the files table https://github.com/HumanCellAtlas/query-service/issues/40

## 10
DCP dashboard - What are all the files submitted since a certain date?

```sql
SELECT *
FROM files
WHERE version > current_date - INTERVAL '4 weeks';
```

## 11
What samples have no files?  Or, perhaps since no files takes it outside of the blue box rework query as:  given a sample UUID are there any bundles and files associated with it?
## 12
On the creation or update of an ingest bundle we would need an event to be created based on the sample.donor.species and the assay.single_cell.method.
## 13
How many (find?) ingest bundles satisfy a query based on sample.donor.species and assay.single_cell.method
## 14
Create events for all ingest bundles that satisfy a query based on sample.donor.species and assay.single_cell.method
## 15
Select all ingest bundles associated with a project. (same as #1?)
## 16
I'm a submitting lab and I submitted some raw data bundles and want to know their status -- have they made it into blue box, been analyzed by green box? If they've been analyzed, where are the analysis bundles? I might ask for status for all samples in a given project, or for some subset of samples in a project. I might want to do the query myself or I might submit a ticket for DCP operations staff to handle the querying.
## 17
I'm a submitting lab and I want a list of all raw data and analysis bundles for all data that my lab has ever submitted, or all submitted during a certain date range, or all analyzed during a certain date range.
## 18
I'm a submitting lab and I just figured out that some of the raw data bundles I submitted are bad -- something went wrong in the lab. I want to find all raw data bundles (and possibly their associated analysis bundles) where the lab processing took place during a certain date range, or used a certain batch of reagents, or that matches some other combination of metadata related to sample prep / lab work.
## 19
Multi'omics analysis. Imagine a future workflow in green box (or a portal) that wants to do integrative analysis on two data types -- say raw imaging data and raw RNA-seq data. We would need a way to query and trigger events whenever a pair of matching bundles (for the same sample id) get deposited. In other words, imaging bundle alone = no event, sequencing bundle alone = no event, imaging + sequencing bundles = event.
## 20
Retreive a list of relesaes that a submission is part of

```sql
/* can't do this without establishing release design first */
```

## 21
Get list of submitters

```sql
SELECT DISTINCT contributors->'contact_name' AS names
FROM projects AS p,
     jsonb_array_elements(p.json->'contributors') AS contributors
WHERE contributors ? 'contact_name'
```

## 22
Get list of submissions for a submitter

```sql
SELECT p.uuid, p.json->'project_core'->>'project_title' AS title
FROM projects AS p
WHERE p.json @> '{"contributors": [{"contact_name": "Aviv,,Regev"}]}'
   OR p.json @> '{"contributors": [{"contact_name": "Sarah,,Teichmann"}]}';
```

## 23
Access all versions of metadata standards
## 24
Get a list of all submissions in progress for a particular submitter.  A submitter that starts a submission with one broker might want/need to continue it with another.
