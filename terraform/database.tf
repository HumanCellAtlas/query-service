locals {
  query_db_username = var.APP_NAME
  query_db_port = "5432"
}

resource "aws_rds_cluster" "query_db" {
  cluster_identifier = "${var.APP_NAME}-${var.STAGE}"
  engine = "aurora-postgresql"
  engine_version = "10.7"
  engine_mode = "serverless"
  db_cluster_parameter_group_name = "default.aurora-postgresql10"
  port = local.query_db_port
  # Requires https://github.com/terraform-providers/terraform-provider-aws/pull/9657
  # Until merged, use `aws rds modify-db-cluster --db-cluster-identifier ID --enable-http-endpoint --apply-immediately`
  # enable_data_api = true
  vpc_security_group_ids = [aws_security_group.query_db_access.id]
  apply_immediately = true
  skip_final_snapshot = true
  master_username = local.query_db_username
  master_password = random_string.placeholder_db_password.result
  tags = {
    managedBy = "terraform"
    project = "dcp"
    env = var.STAGE
    service = var.APP_NAME
    owner = var.OWNER
  }
}

resource "aws_default_vpc" "query_db_vpc" {}

resource "aws_security_group" "query_db_access" {
  name = "${var.APP_NAME}-${var.STAGE}-rds-access"
  ingress {
    from_port = local.query_db_port
    to_port = local.query_db_port
    protocol = "tcp"
    self = true
  }
}

data "aws_subnet_ids" "query_db_subnets" {
  vpc_id = aws_default_vpc.query_db_vpc.id
}

resource "aws_secretsmanager_secret" "query_db_hostname" {
  name = "${var.APP_NAME}/${var.STAGE}/postgresql/hostname"
}

resource "aws_secretsmanager_secret_version" "query_db_hostname" {
  secret_id = aws_secretsmanager_secret.query_db_hostname.id
  secret_string = aws_rds_cluster.query_db.endpoint
}

resource "aws_secretsmanager_secret" "query_db_credentials" {
  name = "${var.APP_NAME}/${var.STAGE}/postgresql/credentials"
}

resource "aws_secretsmanager_secret_version" "query_db_credentials" {
  secret_id = "${aws_secretsmanager_secret.query_db_credentials.id}"
  secret_string = jsonencode({
    "username": local.query_db_username
    "password": random_string.placeholder_db_password.result
  })
}

# The database password is managed out of band.
# Run "make install-secrets" to set the password.
# Run "aws secretsmanager get-secret-value --secret-id dcpquery/dev/postgresql/password" to retrieve it.
# The value below is used only as a placeholder when first setting up the database.

resource "random_string" "placeholder_db_password" {
  length = 32
  special = false
}
