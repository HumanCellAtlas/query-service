terraform {
  backend "s3" {
  }
}

data "external" "aws_config" {
  program = ["cat", ".terraform/aws_config.json"]
}

provider "aws" {
  version = "~> 2.4"
  access_key = "${data.external.aws_config.result.access_key}"
  secret_key = "${data.external.aws_config.result.secret_key}"
  token = "${data.external.aws_config.result.token}"
  region = "${data.external.aws_config.result.region}"
}

provider "external" {
  version = "~> 1.1"
}

provider "template" {
  version = "~> 2.1"
}

module "dcpquery" {
  source = "./terraform"
}
