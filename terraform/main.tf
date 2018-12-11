provider "aws" {
  version             = "~> 1.27.0"
  region              = "us-east-1"
  profile             = "hca"
}

terraform {
  required_version = "=0.11.10"

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
  aws_region          = "${var.aws_region}"
  vpc_id              = "${module.query-service-infra.vpc_id}"
}

module "query-service-infra" {
  source = "modules/query-service-infra"
  domain_name = "${var.domain_name}"
  parent_zone_domain_name = "${var.parent_zone_domain_name}"
  api_id = "${var.api_id}"
  deployment_stage = "${var.deployment_stage}"
  vpc_cidr_block = "${var.vpc_cidr_block}"
}

output "load_data_queue_url" {
  value = "${module.query-service-infra.load_data}"
}

data "aws_subnet_ids" "query_vpc" {
  vpc_id = "${module.query-service-infra.vpc_id}"
}
