resource "aws_s3_bucket" "query-service" {
  bucket = "query-service-${local.account_id}"
  acl = "private"
  force_destroy = "false"
  acceleration_status = "Enabled"
  lifecycle_rule {
    prefix  = "${var.deployment_stage}/query_results/"
    enabled = true

    expiration {
      days = 90
    }
  }
}