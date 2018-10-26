# User Stories and Matching Queries

Query user stories taken from the [Blue Box Queries
Table](https://docs.google.com/spreadsheets/d/1PBMrc0oql4gPpH_cQMqlf7ASNMwePRQZNCutxeSFze8/edit#gid=0)

## 1
Please give me a list of all the contact emails and titles for all the projects, and how many samples and files each has.

### emails
```sql
select p.json->'project_core'->>'project_title' as title, jsonb_agg(contributors->'email') as emails
from projects as p,
     jsonb_array_elements(p.json->'contributors') as contributors
group by 1;
```

### counts
```sql
select p.uuid                                   as project_uuid,
       p.json->'project_core'->>'project_title' as project_title,
       s.json->'organ'->>'text'                 as organ,
       count(1)
from bundles as b
       join specimen_from_organisms as s on s.fqid = ANY(b.file_fqids)
       join projects as p on p.fqid = ANY(b.file_fqids)
group by 1, 2, 3
```

## 2
I’m trying to figure out whether this is a batch effect. Please try to find me examples where the same type of cell was sequenced by the same lab by two different single cell isolation and sequencing techniques. Please also find examples where the same type of cell was sequenced by two different labs using what is supposed to be the same technique.

## 3
Find all bundles specified in release 'X' with tissue type 'Y' Note: could substitute wide variety of other bio constraint, eg, "with coverage gt 10X", etc.

## 4
Find all fastq single cell files that are from a human, that hasn't been processed (no analysis.json file)

```sql
select * from (select f.fqid, f.name
               from bundles as b
                      join donor_organisms as d on d.fqid = ANY(b.file_fqids)
                      join sequencing_protocols as s on s.fqid = ANY(b.file_fqids)
                      join files as f on f.fqid = ANY(b.file_fqids)
               where s.json @> '{"sequencing_approach": {"text": "RNA-Seq"}}'
                 AND d.json @> '{"genus_species": [{"text": "Homo sapiens"}]}'
               group by 1, 2
               having 'analysis_0.json' != ANY(array_agg(f.name))) as unanalyzed
where name like '%.fastq.gz';
```

## 5
What are all the files that were submitted as part of a project? (What are my submissions x timeframe, project name, new study) UI: should be able to page/facet for large lists. Would also like to see the status of each file that is retreived b y the query (may need to break this out into a separate case)

```sql
select p.uuid as project_uuid, f.uuid as file_uuid, f.name as filename
from bundles as b
       join projects as p on p.fqid = ANY(b.file_fqids)
       join files as f on f.fqid = ANY(b.file_fqids)
WHERE f.module_id = 1 /* not a metadata file */
group by 1, 2, 3
```

## 6 & 7
* What are all the files that are the results of analysis of files submitted as part of a project? (overlap with #5 above) Release bundles? “Terminal” or latest bundle
* find all bundles created with a specific method or reference (may want to reprocess the input bundles) May be a 2 step search, 1. Find all results created with a specific version/reference, 2. Use them to find all the source bundles

```sql
select outputs.inputs, outputs.uuid as output_uuid, outputs.process_uuid, f.fqid, f.name, f.json
from files as f
       join (select links->'inputs'                                     as inputs,
                    links->>'process'                                   as process_uuid,
                    jsonb_array_elements_text(links->'outputs') :: uuid as uuid
             from bundles as b
                    join projects p on p.fqid = ANY(b.file_fqids)
                    join links as l on l.fqid = ANY(b.file_fqids),
                  jsonb_array_elements(l.json->'links') as links
             where l.json @> '{"links": [{"protocols": [{"protocol_type": "sequencing_protocol"}]}]}'
               AND p.uuid = '08e7b6ba-5825-47e9-be2d-7978533c5f8c') as outputs on f.uuid = outputs.uuid
```

## 8
What are all of the files of a particular format associated with an particular organ?

```sql
select f.fqid, f.name
from bundles as b
       join files as f on f.fqid = ANY(b.file_fqids)
       join specimen_from_organisms as s on s.fqid = ANY(b.file_fqids)
where s.json @> '{"organ": {"text": "pancreas"}}'
  AND f.name like '%.fastq.gz'
```

## 9
Here's a list of files I'm interested in. What is their total size? Count might also be useful
## 10
DCP dashboard - What are all the files submitted since a certain date?
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
## 21
Get list of submitters
## 22
Get list of submissions for a submitter
## 23
Access all versions of metadata standards
## 24
Get a list of all submissions in progress for a particular submitter.  A submitter that starts a submission with one broker might want/need to continue it with another.
