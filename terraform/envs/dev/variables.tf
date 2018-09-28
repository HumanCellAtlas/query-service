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

locals {
  db_instance_count   = "${var.db_instance_count}"
  db_password         = "${var.db_password}"
  db_username         = "${var.db_username}"
  deployment_stage    = "${var.deployment_stage}"
  lb_subnet_ids       = "${data.aws_subnet_ids.query_vpc.ids}"
  pgbouncer_subnet_id = "${element(data.aws_subnet_ids.query_vpc.ids, 0)}"
  vpc_id              = "${data.aws_vpc.selected.id}"
}