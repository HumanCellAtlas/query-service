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
  source              = "../../modules/database"
  db_instance_count   = "${local.db_instance_count}"
  db_password         = "${local.db_password}"
  db_username         = "${local.db_username}"
  deployment_stage    = "${local.deployment_stage}"
  lb_subnet_ids       = "${local.lb_subnet_ids}"
  pgbouncer_subnet_id = "${local.pgbouncer_subnet_id}"
  vpc_id              = "${local.vpc_id}"
}

module "query-service-infra" {
  source = "../../modules/query-service-infra"
}
