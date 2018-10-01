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

data "aws_vpc" "selected" {
  id = "${var.vpc_id}"
}

data "aws_subnet_ids" "query_vpc" {
  vpc_id = "${data.aws_vpc.selected.id}"
}
