/*
Get list of submissions for a submitter
*/
SELECT p.uuid, p.body->'project_core'->>'project_title' AS title
FROM project AS p
WHERE p.body @> '{"contributors": [{"contact_name": "Aviv,,Regev"}]}'
   OR p.body @> '{"contributors": [{"contact_name": "Sarah,,Teichmann"}]}';
