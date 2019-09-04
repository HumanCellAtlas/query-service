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
  value = "${module.query_db.this_rds_cluster_id}"
}

output "rds_cluster_endpoint" {
  value = "${module.query_db.this_rds_cluster_endpoint}"
}

output "rds_cluster_readonly_endpoint" {
  value = "${module.query_db.this_rds_cluster_reader_endpoint}"
}
