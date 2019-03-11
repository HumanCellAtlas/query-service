module "query_db" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "1.10.0"
  name = "querydb"
  vpc_id = "${aws_default_vpc.query_db_vpc.id}"
  subnets = ["${data.aws_subnet_ids.query_db_subnets.ids}"]
  engine = "aurora-postgresql"
  engine_version = "10.6"
  instance_type = "db.r4.large"
  db_parameter_group_name = "default.aurora-postgresql10"
  db_cluster_parameter_group_name = "default.aurora-postgresql10"
  publicly_accessible = true
  apply_immediately = true
  skip_final_snapshot = true
  username = "${data.aws_secretsmanager_secret_version.query_db_username.secret_string}"
  password = "${data.aws_secretsmanager_secret_version.query_db_password.secret_string}"
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

data "aws_secretsmanager_secret" "query_db_username" {
  name = "${var.APP_NAME}/${var.STAGE}/db/username"
}

data "aws_secretsmanager_secret_version" "query_db_username" {
  secret_id = "${data.aws_secretsmanager_secret.query_db_username.id}"
}

data "aws_secretsmanager_secret" "query_db_password" {
  name = "${var.APP_NAME}/${var.STAGE}/db/password"
}

data "aws_secretsmanager_secret_version" "query_db_password" {
  secret_id = "${data.aws_secretsmanager_secret.query_db_password.id}"
}
