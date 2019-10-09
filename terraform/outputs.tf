output "api_handler_name" {
  value = "${aws_lambda_function.api_handler.function_name}"
}

output "bundle_event_handler_name" {
  value = "${aws_lambda_function.bundle_event_handler.function_name}"
}

output "async_query_handler_name" {
  value = "${aws_lambda_function.async_query_handler.function_name}"
}

output "rds_cluster_id" {
  value = "${aws_rds_cluster.query_db.id}"
}

output "rds_cluster_endpoint" {
  value = "${aws_rds_cluster.query_db.endpoint}"
}

output "rds_cluster_readonly_endpoint" {
  # FIXME: serverless Aurora does not have readonly hostnames. This has been changed to point to the RW endpoint.
  # FIXME: after migrating to data API, retire this secret and use the HTTP endpoint instead.
  value = "${aws_rds_cluster.query_db.endpoint}"
}
