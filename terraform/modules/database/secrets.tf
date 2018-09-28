resource "aws_secretsmanager_secret" "database-secrets" {
  name = "dcp/query-service/${var.deployment_stage}/database"
}

resource "aws_secretsmanager_secret_version" "database-secrets" {
  secret_id = "${aws_secretsmanager_secret.database-secrets.id}"

  secret_string = <<SECRETS_JSON
{
  "database_uri": "postgresql://${aws_rds_cluster.query.master_username}:${aws_rds_cluster.query.master_password}@${aws_rds_cluster.query.endpoint}/${aws_rds_cluster.query.database_name}",
  "pgbouncer_uri": "postgresql://${aws_rds_cluster.query.master_username}:${aws_rds_cluster.query.master_password}@${aws_lb.main.dns_name}/${aws_rds_cluster.query.database_name}"
}
SECRETS_JSON

  depends_on = ["aws_ecs_service.pgbouncer"]
}
