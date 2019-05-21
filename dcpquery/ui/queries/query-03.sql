/*
How many cells from X lab? (denormalized document variant)
*/
SELECT sum(bundle_counts.cell_count)
FROM (SELECT (c->>'total_estimated_cells') :: INTEGER                                      AS cell_count,
             ROW_NUMBER() OVER (PARTITION BY b.bundle_uuid ORDER BY b.bundle_version DESC) AS rk
      FROM bundles AS b,
           jsonb_array_elements(b.json->'cell_suspensions') AS c,
           jsonb_array_elements(b.json->'projects'->0->'contributors') AS contribs
      WHERE contribs->>'laboratory' LIKE '%Sarah Teichmann%'
        AND NOT b.json ? 'analysis_files') AS bundle_counts
WHERE bundle_counts.rk = 1;
/*
Here, `WHERE ... NOT b.json ? 'analysis_files'` is used to avoid double counting cells from analysis bundles.
*/
