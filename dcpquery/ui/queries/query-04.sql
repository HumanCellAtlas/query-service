/*
[Not ready] Average number of cells per experiment for lab X? (denormalized document variant)
*/
SELECT avg(project_counts.cell_count)
FROM (SELECT bundle_counts.project_title, sum(bundle_counts.cell_count) AS cell_count
      FROM (SELECT p->'project_core'->>'project_title'                                           AS project_title,
                   (c->>'total_estimated_cells') :: INTEGER                                      AS cell_count,
                   ROW_NUMBER() OVER (PARTITION BY b.uuid ORDER BY b.version DESC) AS rk
            FROM bundles AS b,
                 jsonb_array_elements(b.aggregate_metadata->'projects') AS p,
                 jsonb_array_elements(b.aggregate_metadata->'cell_suspensions') AS c,
                 jsonb_array_elements(b.aggregate_metadata->'projects'->0->'contributors') AS contribs
            WHERE contribs->>'laboratory' LIKE '%Sarah Teichmann%'
              AND NOT b.aggregate_metadata ? 'analysis_files') AS bundle_counts
      WHERE bundle_counts.rk = 1
      GROUP BY 1) AS project_counts;
/*
Notice here that the `PARTITION BY b.bundle_uuid ORDER BY b.bundle_version DESC` and `WHERE bundle_counts.rk = 1` is used to select the most recent version of all bundles from Sarah.
*/
