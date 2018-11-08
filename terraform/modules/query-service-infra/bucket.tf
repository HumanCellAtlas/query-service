resource "aws_s3_bucket" "lambda_deployments" {
  bucket = "query-service-lambda-deployment-${var.deployment_stage}"
  acl = "private"
  force_destroy = "false"
  acceleration_status = "Enabled"
}