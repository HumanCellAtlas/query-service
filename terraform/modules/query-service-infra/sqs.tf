
resource "aws_sqs_queue" "load_data_queue" {
  name                      = "dcp-query-data-input-queue-${var.deployment_stage}"
//  Queue visibility timeout must be larger than (triggered lambda) function timeout
  visibility_timeout_seconds = 900
  message_retention_seconds = 86400
  redrive_policy            = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.deadletter_queue.arn}\",\"maxReceiveCount\":4}"

}

resource "aws_sqs_queue" "async_query_queue" {
  name                      = "dcp-query-async-query-queue-${var.deployment_stage}"
  visibility_timeout_seconds = 900
  message_retention_seconds = 86400
  redrive_policy            = "{\"deadLetterTargetArn\":\"${aws_sqs_queue.deadletter_queue.arn}\",\"maxReceiveCount\":4}"

}

resource "aws_sqs_queue" "deadletter_queue" {
  name                      = "dcp-query-deadletter-queue-${var.deployment_stage}"
  message_retention_seconds = 1209600
}

data "template_file" "load_data_queue_policy_doc" {
  template = "${file("${path.module}/../../../iam/policy-templates/sqs_queue.json")}"
  vars = {
    queue_arn = "${aws_sqs_queue.load_data_queue.arn}",
    lambda_arn = "arn:aws:lambda:*:*:function:query-load-data-${var.deployment_stage}"
  }
}

resource "aws_sqs_queue_policy" "load_data_queue_access" {
  queue_url = "${aws_sqs_queue.load_data_queue.id}"
  policy = "${data.template_file.load_data_queue_policy_doc.rendered}"
}

data "template_file" "async_query_queue_policy_doc" {
  template = "${file("${path.module}/../../../iam/policy-templates/sqs_queue.json")}"
  vars = {
    queue_arn = "${aws_sqs_queue.async_query_queue.arn}",
    lambda_arn = "arn:aws:lambda:*:*:function:query-create-async-query-${var.deployment_stage}"
  }
}

resource "aws_sqs_queue_policy" "async_query_queue_access" {
  queue_url = "${aws_sqs_queue.async_query_queue.id}"
  policy = "${data.template_file.async_query_queue_policy_doc.rendered}"
}


resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  batch_size = 1
  event_source_arn  = "${aws_sqs_queue.async_query_queue.arn}"
  enabled           = true
  function_name     = "${aws_lambda_function.query_create_async_query_lambda.arn}"
}

output "load_data" {
  value = "${aws_sqs_queue.load_data_queue.id}"
}

output "async_query" {
  value = "${aws_sqs_queue.async_query_queue.id}"
}
