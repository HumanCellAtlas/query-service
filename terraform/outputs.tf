output "api_handler_name" {
  value = aws_lambda_function.api_handler.function_name
}

output "bundle_event_handler_name" {
  value = aws_lambda_function.bundle_event_handler.function_name
}

output "async_query_handler_name" {
  value = aws_lambda_function.async_query_handler.function_name
}

output "rds_cluster_id" {
  value = aws_rds_cluster.query_db.id
}

output "rds_cluster_endpoint" {
  value = aws_rds_cluster.query_db.endpoint
}
