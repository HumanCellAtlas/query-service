/*
Please give me a list of all the contact emails and titles for all the projects, and how many samples (specimens) and sequencing files each project has.
*/
SELECT p.body->'project_core'->>'project_title' AS title, jsonb_agg(contributors->'email') AS emails
FROM project AS p,
     jsonb_array_elements(p.body->'contributors') AS contributors
GROUP BY 1;
