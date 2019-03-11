resource "aws_sqs_queue" "bundle_events" {
  name = "${var.BUNDLE_EVENTS_QUEUE_NAME}"
  visibility_timeout_seconds = 900
}

resource "aws_sqs_queue" "async_queries" {
  name = "${var.ASYNC_QUERIES_QUEUE_NAME}"
  visibility_timeout_seconds = 900
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

resource "aws_cloudformation_stack" "lambda" {
  name = "${var.APP_NAME}"
  capabilities = ["CAPABILITY_IAM"]
  parameters {
  }

  template_body = "${file("dist/cloudformation.json")}"
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
  api_id = "${aws_cloudformation_stack.lambda.outputs["RestAPIId"]}"
  stage_name = "api"
  domain_name = "${var.API_DOMAIN_NAME}"
}

resource "aws_s3_bucket" "query_service_bucket" {
  bucket = "${var.APP_NAME}-${var.STAGE}-${var.AWS_ACCOUNT_ID}"
  acl    = "private"
}
