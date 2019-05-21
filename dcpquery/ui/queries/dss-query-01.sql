/*
Please give me a list of all the contact emails and titles for all the projects, and how many samples (specimens) and sequencing files each project has.
*/
SELECT p.json->'project_core'->>'project_title' AS title, jsonb_agg(contributors->'email') AS emails
FROM projects AS p,
     jsonb_array_elements(p.json->'contributors') AS contributors
GROUP BY 1;
