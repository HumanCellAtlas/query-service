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

resource "aws_iam_role_policy" "query_load_data_lambda" {
  name = "query-load-data-${var.deployment_stage}"
  role = "${aws_iam_role.query_load_data_lambda.name}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaPolicy",
      "Action": [
        "events:*",
        "iam:ListAttachedRolePolicies",
        "iam:ListRolePolicies",
        "iam:ListRoles",
        "iam:PassRole"
      ],
      "Resource": "*",
      "Effect": "Allow"
    },
    {
      "Sid": "LambdaLogging",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": [
        "arn:aws:logs:*:*:*"
      ],
      "Effect": "Allow"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:query/${var.deployment_stage}/*",
        "arn:aws:secretsmanager:${local.aws_region}:${local.account_id}:secret:dcp/query/${var.deployment_stage}/database-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ChangeMessageVisibility",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource": [
        "arn:aws:sqs:*:*:${aws_sqs_queue.load_data_queue.name}"
      ]
    },
    {
      "Effect": "Allow",
      "Action":["s3:GetObject"],
      "Resource": [
        "arn:aws:s3:::*",
        "arn:aws:s3:::*/*"
        ]
    }
  ]
}
EOF
}

output "query_load_data_lambda_role_arn" {
  value = "${aws_iam_role.query_load_data_lambda.arn}"
}


resource "aws_lambda_function" "query_load_data_lambda" {
  function_name    = "query-load-data-${var.deployment_stage}"
  s3_bucket        = "${aws_s3_bucket.lambda_deployments.id}"
  s3_key           = "${var.deployment_stage}/load_data/load_data.zip"
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
