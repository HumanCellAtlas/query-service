/*
How many experiments from lab X?  (denormalized document variant)
*/
SELECT count(DISTINCT p.body->'project_core'->'project_title')
FROM project AS p,
     jsonb_array_elements(p.body->'contributors') AS contribs
WHERE contribs->>'laboratory' LIKE '%Sarah Teichmann%';
