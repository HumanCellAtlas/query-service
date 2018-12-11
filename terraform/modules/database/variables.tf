gvariable "pgbouncer_subnet_id" {
  type = "string"
}

variable "lb_subnet_ids" {
  type = "list"
}

variable "vpc_id" {
  type = "string"
}

variable "deployment_stage" {
  type    = "string"
  default = "dev"
}

variable "db_username" {
  type    = "string"
  default = "master"
}

variable "db_password" {
  type    = "string"
}

variable "db_instance_count" {
  type    = "string"
  default = 2
}
