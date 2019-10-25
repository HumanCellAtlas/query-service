terraform {
  required_version = ">= 0.12.12"
  backend "s3" {
  }
}

provider "aws" {
  version = "~> 2.33"
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

output "dcpquery" {
  value = module.dcpquery
}
