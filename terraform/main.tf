provider "aws" {
  version             = "~> 1.27.0"
  region              = "us-east-1"
  profile             = "hca"
}
# cant interpolate the key for the s3 bucket -> need to hard code for each deployment stage/environment
terraform {
  required_version = "~>0.11.7"

  backend "s3" {
    bucket = "org-humancellatlas-861229788715-terraform"
    key = "query-service/dev/state.tfstate"
    encrypt = true
    region  = "us-east-1"
    profile = "hca-id"
  }
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
