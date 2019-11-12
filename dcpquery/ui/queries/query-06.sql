/*
Get the fqids of all of the bundles a particular file belongs to
*/

SELECT bundle_fqid FROM bundle_file_links WHERE file_fqid=:file_fqid