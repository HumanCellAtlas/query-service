/*
Get the fqids of all files in project
*/
SELECT file_fqid FROM project_file_links WHERE project_fqid=:project_fqid