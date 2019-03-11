output "api_handler_name" {
  value = "${aws_cloudformation_stack.lambda.outputs["APIHandlerName"]}"
}

output "bundle_event_handler_name" {
  value = "${aws_cloudformation_stack.lambda.outputs["BundleEventHandlerName"]}"
}

output "async_query_handler_name" {
  value = "${aws_cloudformation_stack.lambda.outputs["AsyncQueryHandlerName"]}"
}

output "api_endpoint_url" {
  value = "${aws_cloudformation_stack.lambda.outputs["EndpointURL"]}"
}

output "rds_cluster_endpoint" {
  value = "${module.query_db.this_rds_cluster_endpoint}"
}

output "rds_cluster_readonly_endpoint" {
  value = "${module.query_db.this_rds_cluster_reader_endpoint}"
}
