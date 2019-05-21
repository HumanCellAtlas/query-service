/*
How many experiments from lab X?  (denormalized document variant)
*/
SELECT count(DISTINCT p.json->'project_core'->'project_title')
FROM projects AS p,
     jsonb_array_elements(p.json->'contributors') AS contribs
WHERE contribs->>'laboratory' LIKE '%Sarah Teichmann%';
