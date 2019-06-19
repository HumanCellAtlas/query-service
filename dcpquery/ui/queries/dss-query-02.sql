/*
Get list of submitters
*/
SELECT DISTINCT contributors->'contact_name' AS names
FROM project AS p,
     jsonb_array_elements(p.body->'contributors') AS contributors
WHERE contributors ? 'contact_name'
