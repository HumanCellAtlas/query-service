variable "domain_name" {
  type = "string"
}

variable "parent_zone_domain_name" {
  type = "string"
}

variable "api_id" {
  type = "string"
}

variable "deployment_stage" {
  type = "string"
}

//variable "vpc_cidr_block" {
//  type = "string"
//}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}