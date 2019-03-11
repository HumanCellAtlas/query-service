terraform {
  backend "s3" {
  }
}

data "external" "aws_config" {
  program = ["make", "get-config"]
}

provider "aws" {
  access_key = "${data.external.aws_config.result.access_key}"
  secret_key = "${data.external.aws_config.result.secret_key}"
  token = "${data.external.aws_config.result.token}"
  region = "${data.external.aws_config.result.region}"
}

module "dcpquery" {
  source = "./terraform"
}
