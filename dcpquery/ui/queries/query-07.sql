/*
Get the fqids of all of the files that are a specific version of a schema type
*/

SELECT fqid FROM files_all_versions
WHERE dcp_schema_type_name=:schema_type_name
AND schema_major_version=:major_version
AND  schema_minor_version=:minor_version

/*
As the Files materialized view only contains the latest version of all files
it is necessary to query the underlying files_all_versions table if you are
searching for previous schema versions
*/