/*
Get list of submitters
*/
SELECT DISTINCT contributors->'contact_name' AS names
FROM projects AS p,
     jsonb_array_elements(p.json->'contributors') AS contributors
WHERE contributors ? 'contact_name'
