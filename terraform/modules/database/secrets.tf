resource "aws_secretsmanager_secret" "database-secrets" {
  name = "dcp/query/${var.deployment_stage}/database"
}

# TODO: automate creation of test database
resource "aws_secretsmanager_secret_version" "database-secrets" {
  secret_id = "${aws_secretsmanager_secret.database-secrets.id}"

  secret_string = <<SECRETS_JSON
{
  "user": "${aws_rds_cluster.query.master_username}",
  "password": "${aws_rds_cluster.query.master_password}",
  "database": "${aws_rds_cluster.query.database_name}",
  "rds_dns_name": "${aws_rds_cluster.query.endpoint}",
  "pgbouncer_dns_name": "${aws_lb.main.dns_name}"
}
SECRETS_JSON

  depends_on = ["aws_ecs_service.pgbouncer"]
}
