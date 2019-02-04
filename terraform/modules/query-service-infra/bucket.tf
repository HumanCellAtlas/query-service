resource "aws_s3_bucket" "query-service" {
  bucket = "query-service-${local.account_id}"
  acl = "private"
  force_destroy = "false"
  acceleration_status = "Enabled"
  lifecycle_rule {
    prefix  = "predev/query_results/"
    enabled = true

    expiration {
      days = 90
    }
  }
  lifecycle_rule {
    prefix  = "dev/query_results/"
    enabled = true

    expiration {
      days = 90
    }
  }
  lifecycle_rule {
    prefix  = "integration/query_results/"
    enabled = true

    expiration {
      days = 90
    }
  }
  lifecycle_rule {
    prefix  = "staging/query_results/"
    enabled = true

    expiration {
      days = 90
    }
  }
  lifecycle_rule {
    prefix  = "prod/query_results/"
    enabled = true

    expiration {
      days = 90
    }
  }
}