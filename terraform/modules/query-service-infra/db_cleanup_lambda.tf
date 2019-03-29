resource "aws_iam_role" "query_daily_db_cleanup_lambda" {
  name = "query-daily-db-cleanup-${var.deployment_stage}"
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

data "template_file" "db_cleanup_lambda_policy_doc" {
  template = "${file("${path.module}/../../../iam/policy-templates/db_cleanup_lambda.json")}"
  vars = {
    logs_group_arn = "arn:aws:logs:${local.aws_region}:${local.account_id}:log-group:/aws/lambda/query-daily-db-cleanup-${var.deployment_stage}",
    logs_arn = "arn:aws:logs:${local.aws_region}:${local.account_id}:log-group:/aws/lambda/query-daily-db-cleanup-${var.deployment_stage}:*:*",
    secrets_arn = "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:query/${var.deployment_stage}/*",
    db_secrets_arn = "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:dcp/query/${var.deployment_stage}/database-*"
  }
}

resource "aws_iam_role_policy" "db_cleanup_lambda_access" {
  role = "${aws_iam_role.query_daily_db_cleanup_lambda.name}"
  policy = "${data.template_file.db_cleanup_lambda_policy_doc.rendered}"
}

resource "aws_lambda_function" "query_daily_db_cleanup_lambda" {
  function_name    = "query-daily-db-cleanup-${var.deployment_stage}"
  s3_bucket        = "${aws_s3_bucket.query-service.id}"
  s3_key           = "${var.deployment_stage}/lambda_deployments/db_cleanup/db_cleanup.zip"
  role             = "arn:aws:iam::${local.account_id}:role/query-daily-db-cleanup-${var.deployment_stage}"
  handler          = "app.handler"
  runtime          = "python3.6"
  memory_size      = 128
  timeout          = 300

  environment {
    variables = {
      DEPLOYMENT_STAGE = "${var.deployment_stage}",
      AWS_ACCOUNT_ID = "${local.account_id}"

    }
  }
}

resource "aws_cloudwatch_event_rule" "daily" {
    name = "query-every-day-${var.deployment_stage}"
    description = "Fires every day at 13:00 UTC"
    schedule_expression = "cron(0 13 * * ? *)"
}

resource "aws_cloudwatch_event_target" "query_daily_db_cleanup" {
    rule = "${aws_cloudwatch_event_rule.daily.name}"
    target_id = "query_daily_db_cleanup_lambda"
    arn = "${aws_lambda_function.query_daily_db_cleanup_lambda.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_db_cleanup" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.query_daily_db_cleanup_lambda.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.daily.arn}"
}
