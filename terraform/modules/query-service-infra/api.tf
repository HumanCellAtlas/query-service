// DNS
data "aws_route53_zone" "primary" {
  name         = "${var.parent_zone_domain_name}."
}

resource "aws_acm_certificate" "cert" {
  domain_name = "${var.domain_name}"
  validation_method = "DNS"
}

resource "aws_route53_record" "cert_validation" {
  name = "${aws_acm_certificate.cert.domain_validation_options.0.resource_record_name}"
  type = "${aws_acm_certificate.cert.domain_validation_options.0.resource_record_type}"
  zone_id = "${data.aws_route53_zone.primary.id}"
  records = ["${aws_acm_certificate.cert.domain_validation_options.0.resource_record_value}"]
  ttl = 60
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn = "${aws_acm_certificate.cert.arn}"
  validation_record_fqdns = ["${aws_route53_record.cert_validation.fqdn}"]
}

resource "aws_api_gateway_domain_name" "query_api" {
  domain_name = "${var.domain_name}"
  certificate_arn = "${aws_acm_certificate.cert.arn}"
}

resource "aws_route53_record" "query" {
  zone_id = "${data.aws_route53_zone.primary.id}" # See aws_route53_zone for how to create this

  name = "${var.domain_name}"
  type = "A"

  alias {
    name                   = "${aws_api_gateway_domain_name.query_api.cloudfront_domain_name}"
    zone_id                = "${aws_api_gateway_domain_name.query_api.cloudfront_zone_id}"
    evaluate_target_health = false
  }
}

resource "aws_api_gateway_base_path_mapping" "query_api" {
  api_id      = "${var.api_id}"
  stage_name  = "${var.deployment_stage}"
  domain_name = "${aws_api_gateway_domain_name.query_api.domain_name}"
}