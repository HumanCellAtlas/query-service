resource "aws_iam_role" "query_create_async_query_lambda" {
  name = "query-create-async-query-${var.deployment_stage}"
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

data "template_file" "async_query_lambda_policy_doc" {
  template = "${file("${path.module}/../../../iam/policy-templates/async_query_lambda.json")}"
  vars = {
    logs_arn = "arn:aws:logs:*:*:*",
    secrets_arn = "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:query/${var.deployment_stage}/*",
    db_secrets_arn = "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:dcp/query/${var.deployment_stage}/database-*",
    queue_arn = "arn:aws:sqs:*:*:${aws_sqs_queue.async_query_queue.name}",
    s3_arn = "arn:aws:s3:::*"
    s3_object_arn = "arn:aws:s3:::*/*"
  }
}

resource "aws_iam_role_policy" "async_query_lambda_access" {
  role = "${aws_iam_role.query_create_async_query_lambda.name}"
  policy = "${data.template_file.async_query_lambda_policy_doc.rendered}"
}

resource "aws_lambda_function" "query_create_async_query_lambda" {
  function_name    = "query-create-async-query-${var.deployment_stage}"
  s3_bucket        = "${aws_s3_bucket.query-service.id}"
  s3_key           = "${var.deployment_stage}/lambda_deployments/create_async_query/create_async_query.zip"
  role             = "arn:aws:iam::${local.account_id}:role/query-create-async-query-${var.deployment_stage}"
  handler          = "app.handler"
  runtime          = "python3.6"
  memory_size      = 960
  timeout          = 900

  environment {
    variables = {
      DEPLOYMENT_STAGE = "${var.deployment_stage}"
      AWS_ACCOUNT_ID = "${local.account_id}"
    }
  }
}
