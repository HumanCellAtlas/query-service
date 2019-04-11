terraform {
  backend "s3" {
  }
}

provider "aws" {
  version = "~> 2.4"
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
