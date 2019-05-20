/*
[Not ready] Find all pancreas cells from women age 40-50 (denormalized document variant)
*/
SELECT b.uuid
FROM bundles AS b,
     LATERAL jsonb_array_elements(b.aggregate_metadata->'donor_organisms') AS o
WHERE b.aggregate_metadata @> '{"specimen_from_organisms": [{"organ": {"text": "pancreas"}}]}'
  AND b.aggregate_metadata @> '{"donor_organisms": [{"sex": "female"}, {"genus_species":[{"text": "Homo sapiens"}]}]}'
  AND o->>'organism_age' NOT LIKE '%-%'
  AND COALESCE(o->>'organism_age', '0') :: INTEGER BETWEEN 40 AND 50;
