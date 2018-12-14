variable "db_username" {
  type = "string"
}

variable "db_password" {
  type = "string"
}

variable "db_instance_count" {
  type = "string"
}

variable "deployment_stage" {
  type = "string"
}

variable "vpc_id" {
  type = "string"
}

variable "domain_name" {
  type = "string"
}

variable "parent_zone_domain_name" {
  type = "string"
}

variable "api_id" {
  type = "string"
}

data "aws_vpc" "selected" {
  id = "${var.vpc_id}"
}

variable "aws_region" {
  type = "string"
}

data "aws_subnet_ids" "query_vpc" {
  vpc_id = "${data.aws_vpc.selected.id}"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

