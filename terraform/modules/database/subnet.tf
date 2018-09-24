resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "query_db_subnet_group_${var.env}"
  subnet_ids = ["${var.lb_subnet_ids}"]

  tags {
    Name = "DCP Query ${var.env} DB Subnet Group"
  }
}
