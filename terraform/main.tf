provider "aws" {
  version             = "~> 1.27.0"
  region              = "us-east-1"
  profile             = "hca"
}

terraform {
  required_version = "=0.11.7"

  backend "s3" {}
}

module "database" {
  source              = "modules/database"
  db_instance_count   = "${var.db_instance_count}"
  db_password         = "${var.db_password}"
  db_username         = "${var.db_username}"
  deployment_stage    = "${var.deployment_stage}"
  lb_subnet_ids       = "${data.aws_subnet_ids.query_vpc.ids}"
  pgbouncer_subnet_id = "${element(data.aws_subnet_ids.query_vpc.ids, 0)}"
  vpc_id              = "${data.aws_vpc.selected.id}"
}

module "query-service-infra" {
  source = "modules/query-service-infra"
}