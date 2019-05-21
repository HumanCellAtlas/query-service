/*
Get list of submissions for a submitter
*/
SELECT p.uuid, p.json->'project_core'->>'project_title' AS title
FROM projects AS p
WHERE p.json @> '{"contributors": [{"contact_name": "Aviv,,Regev"}]}'
   OR p.json @> '{"contributors": [{"contact_name": "Sarah,,Teichmann"}]}';
