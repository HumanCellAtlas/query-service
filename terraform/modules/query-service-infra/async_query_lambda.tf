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

resource "aws_iam_role_policy" "query_create_async_query_lambda" {
  name = "query-create-async-query-${var.deployment_stage}"
  role = "${aws_iam_role.query_create_async_query_lambda.name}"
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
        "arn:aws:sqs:*:*:${aws_sqs_queue.async_query_queue.name}"
      ]
    },
    {
      "Effect": "Allow",
      "Action":["s3:GetObject", "s3:PutObject", "s3:PutObjectAcl"],
      "Resource": [
        "arn:aws:s3:::*",
        "arn:aws:s3:::*/*"
        ]
    }
  ]
}
EOF
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
