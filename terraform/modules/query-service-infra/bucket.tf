resource "aws_s3_bucket" "query-service" {
  bucket = "query-service-${local.account_id}"
  acl = "private"
  force_destroy = "false"
  acceleration_status = "Enabled"
}