
resource "aws_sqs_queue" "load_data_queue" {
  name                      = "dcp-query-data-input-queue-${var.deployment_stage}"
//  Queue visibility timeout must be larger than (triggered lambda) function timeout
  visibility_timeout_seconds = 900
  message_retention_seconds = 86400
  redrive_policy            = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.deadletter_queue.arn}\",\"maxReceiveCount\":4}"

}

output "load_data" {
  value = "${aws_sqs_queue.load_data_queue.id}"
}


resource "aws_sqs_queue" "long_query_queue" {
  name                      = "dcp-query-long-query-queue-${var.deployment_stage}"
//  Queue visibility timeout must be larger than (triggered lambda) function timeout
  visibility_timeout_seconds = 900
  message_retention_seconds = 86400
  redrive_policy            = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.deadletter_queue.arn}\",\"maxReceiveCount\":4}"

}

output "long_query" {
  value = "${aws_sqs_queue.long_query_queue.id}"
}

resource "aws_sqs_queue" "deadletter_queue" {
  name                      = "dcp-query-data-input-deadletter-queue-${var.deployment_stage}"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue_policy" "load_data_queue_access" {
  queue_url = "${aws_sqs_queue.load_data_queue.id}"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "sqspolicy",
  "Statement": [
  {
      "Sid": "First",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "SQS:SendMessage",
      "Resource": "${aws_sqs_queue.load_data_queue.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateEventSourceMapping",
        "lambda:ListEventSourceMappings",
        "lambda:ListFunction"
      ],
      "Resource": [
        "arn:aws:lambda:*:*:function:query-load-data-${var.deployment_stage}"
      ]
    }
  ]
}
POLICY
}

resource "aws_sqs_queue_policy" "long_query_queue_access" {
  queue_url = "${aws_sqs_queue.long_query_queue.id}"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "sqspolicy",
  "Statement": [
  {
      "Sid": "First",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "SQS:SendMessage",
      "Resource": "${aws_sqs_queue.long_query_queue.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateEventSourceMapping",
        "lambda:ListEventSourceMappings",
        "lambda:ListFunction"
      ],
      "Resource": [
        "arn:aws:lambda:*:*:function:query-load-data-${var.deployment_stage}"
      ]
    }
  ]
}
POLICY
}

resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  batch_size = 1
  event_source_arn  = "${aws_sqs_queue.load_data_queue.arn}"
  enabled           = true
  function_name     = "${aws_lambda_function.query_load_data_lambda.arn}"
}