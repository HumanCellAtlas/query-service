resource "aws_iam_role" "query_load_data_lambda" {
  name = "query-load-data-${var.deployment_stage}"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

data "template_file" "load_data_lambda_policy_doc" {
  template = "${file("${path.module}/../../../iam/policy-templates/load_data_lambda.json")}"
  vars = {
    logs_arn = "arn:aws:logs:*:*:*",
    secrets_arn = "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:query/${var.deployment_stage}/*",
    db_secrets_arn = "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:dcp/query/${var.deployment_stage}/database-*",
    queue_arn = "arn:aws:sqs:*:*:${aws_sqs_queue.load_data_queue.name}",
    s3_arn = "arn:aws:s3:::*"
    s3_object_arn = "arn:aws:s3:::*/*"
  }
}

resource "aws_iam_role_policy" "load_data_lambda_access" {
  role = "${aws_iam_role.query_load_data_lambda.name}"
  policy = "${data.template_file.load_data_lambda_policy_doc.rendered}"
}

resource "aws_lambda_function" "query_load_data_lambda" {
  function_name    = "query-load-data-${var.deployment_stage}"
  s3_bucket        = "${aws_s3_bucket.query-service.id}"
  s3_key           = "${var.deployment_stage}/lambda_deployments/load_data/load_data.zip"
  role             = "arn:aws:iam::${local.account_id}:role/query-load-data-${var.deployment_stage}"
  handler          = "app.load_data"
  runtime          = "python3.6"
  memory_size      = 960
  timeout          = 900

  environment {
    variables = {
      DEPLOYMENT_STAGE = "${var.deployment_stage}"
    }
  }
}
