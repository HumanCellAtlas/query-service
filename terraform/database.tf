module "query_db" {
  source = "github.com/chanzuckerberg/terraform-aws-rds-aurora"
  name = "${var.APP_NAME}-${var.STAGE}"
  vpc_id = "${aws_default_vpc.query_db_vpc.id}"
  subnets = data.aws_subnet_ids.query_db_subnets.ids
  engine = "aurora-postgresql"
  engine_version = "10.7"
  instance_type = "db.r4.large"
  db_parameter_group_name = "default.aurora-postgresql10"
  db_cluster_parameter_group_name = "default.aurora-postgresql10"
  publicly_accessible = true
  apply_immediately = true
  skip_final_snapshot = true
  username = "${aws_secretsmanager_secret_version.query_db_username.secret_string}"
  tags = {
    managedBy = "terraform"
    project = "dcp"
    env = "${var.STAGE}"
    service = "${var.APP_NAME}"
    owner = "${var.OWNER}"
  }
}

resource "aws_default_vpc" "query_db_vpc" {}

resource "aws_security_group_rule" "query_db_access" {
  type = "ingress"
  from_port = "${module.query_db.this_rds_cluster_port}"
  to_port = "${module.query_db.this_rds_cluster_port}"
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = "${module.query_db.this_security_group_id}"
}

data "aws_subnet_ids" "query_db_subnets" {
  vpc_id = "${aws_default_vpc.query_db_vpc.id}"
}

resource "aws_secretsmanager_secret" "query_db_hostname" {
  name = "${var.APP_NAME}/${var.STAGE}/postgresql/hostname"
}

resource "aws_secretsmanager_secret_version" "query_db_hostname" {
  secret_id = "${aws_secretsmanager_secret.query_db_hostname.id}"
  secret_string = "${module.query_db.this_rds_cluster_endpoint}"
}

resource "aws_secretsmanager_secret" "query_db_readonly_hostname" {
  name = "${var.APP_NAME}/${var.STAGE}/postgresql/readonly_hostname"
}

resource "aws_secretsmanager_secret_version" "query_db_readonly_hostname" {
  secret_id = "${aws_secretsmanager_secret.query_db_readonly_hostname.id}"
  secret_string = "${module.query_db.this_rds_cluster_reader_endpoint}"
}

resource "aws_secretsmanager_secret" "query_db_username" {
  name = "${var.APP_NAME}/${var.STAGE}/postgresql/username"
}

resource "aws_secretsmanager_secret_version" "query_db_username" {
  secret_id = "${aws_secretsmanager_secret.query_db_username.id}"
  secret_string = "${var.APP_NAME}"
}

resource "aws_secretsmanager_secret" "query_db_password" {
  name = "${var.APP_NAME}/${var.STAGE}/postgresql/password"
}

# The database password is managed out of band.
# Run "make install-secrets" to set the password.
# Run "aws secretsmanager get-secret-value --secret-id dcpquery/dev/postgresql/password" to retrieve it.
