/*
Find all pancreas cells from women age 40-50 (denormalized document variant)
*/
SELECT b.bundle_uuid
FROM bundles AS b,
     LATERAL jsonb_array_elements(b.json->'donor_organisms') AS o
WHERE b.json @> '{"specimen_from_organisms": [{"organ": {"text": "pancreas"}}]}'
  AND b.json @> '{"donor_organisms": [{"sex": "female"}, {"genus_species":[{"text": "Homo sapiens"}]}]}'
  AND o->>'organism_age' NOT LIKE '%-%'
  AND COALESCE(o->>'organism_age', '0') :: INTEGER BETWEEN 40 AND 50;
