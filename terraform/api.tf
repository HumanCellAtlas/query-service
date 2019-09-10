resource "aws_sqs_queue" "bundle_events" {
  name = "${var.BUNDLE_EVENTS_QUEUE_NAME}"
  visibility_timeout_seconds = 900
  redrive_policy = jsonencode({
    "deadLetterTargetArn" = "${aws_sqs_queue.dlq.arn}",
    "maxReceiveCount" = 5
  })
}

resource "aws_sqs_queue" "async_queries" {
  name = "${var.ASYNC_QUERIES_QUEUE_NAME}"
  visibility_timeout_seconds = 900
  redrive_policy = jsonencode({
    "deadLetterTargetArn" = "${aws_sqs_queue.dlq.arn}",
    "maxReceiveCount" = 5
  })
}

resource "aws_sqs_queue" "dlq" {
  name = "${var.APP_NAME}-${var.STAGE}-dlq"
}

data "template_file" "bundle_events_queue_policy_doc" {
  template = "${file("${path.module}/../iam/policy-templates/sqs_queue.json")}"
  vars = {
    queue_arn = "${aws_sqs_queue.bundle_events.arn}"
  }
}

data "template_file" "async_queries_queue_policy_doc" {
  template = "${file("${path.module}/../iam/policy-templates/sqs_queue.json")}"
  vars = {
    queue_arn = "${aws_sqs_queue.async_queries.arn}"
  }
}

resource "aws_sqs_queue_policy" "bundle_events_policy" {
  queue_url = "${aws_sqs_queue.bundle_events.id}"
  policy = "${data.template_file.bundle_events_queue_policy_doc.rendered}"
}

resource "aws_sqs_queue_policy" "async_queries_policy" {
  queue_url = "${aws_sqs_queue.async_queries.id}"
  policy = "${data.template_file.async_queries_queue_policy_doc.rendered}"
}

data "aws_acm_certificate" "api_cert" {
  domain = "${var.API_DOMAIN_NAME}"
}

data "aws_route53_zone" "api_dns_zone" {
  name = "${var.API_DNS_ZONE}"
}

resource "aws_api_gateway_domain_name" "api_apigwcdn" {
  certificate_arn = "${data.aws_acm_certificate.api_cert.arn}"
  domain_name = "${var.API_DOMAIN_NAME}"
}

resource "aws_route53_record" "api_dns_record" {
  name = "${aws_api_gateway_domain_name.api_apigwcdn.domain_name}"
  type = "A"
  zone_id = "${data.aws_route53_zone.api_dns_zone.id}"

  alias {
    evaluate_target_health = true
    name = "${aws_api_gateway_domain_name.api_apigwcdn.cloudfront_domain_name}"
    zone_id = "${aws_api_gateway_domain_name.api_apigwcdn.cloudfront_zone_id}"
  }
}

resource "aws_api_gateway_base_path_mapping" "api_bpm" {
  api_id = "${aws_api_gateway_deployment.rest_api.rest_api_id}"
  stage_name = "${var.STAGE}"
  domain_name = "${var.API_DOMAIN_NAME}"
}

resource "aws_s3_bucket" "query_service_bucket" {
  bucket = "${var.SERVICE_S3_BUCKET}"
  acl    = "private"

  lifecycle_rule {
    id = "job_result_docs"
    enabled = true
    prefix = "job_result/"
    expiration {
      days = 30
    }
  }

  lifecycle_rule {
    id = "job_status_docs"
    enabled = true
    prefix = "job_status/"
    expiration {
      days = 30
    }
  }
}

resource "aws_secretsmanager_secret" "webhook_auth_config" {
  name = "${var.APP_NAME}/${var.STAGE}/webhook-auth-config"
}

resource "aws_secretsmanager_secret" "gcp_credentials" {
  name = "${var.APP_NAME}/${var.STAGE}/gcp-credentials.json"
}

resource "aws_secretsmanager_secret" "gitlab_api" {
  name = "${var.APP_NAME}/gitlab-api"
}

resource "aws_secretsmanager_secret" "gitlab_token" {
  name = "${var.APP_NAME}/gitlab-token"
}
