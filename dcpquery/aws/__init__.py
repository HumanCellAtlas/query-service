import json

from . import clients, resources


def send_sqs_message(queue_name, message):
    print(queue_name)
    print(message)
    q = resources.sqs.Queue(clients.sqs.get_queue_url(QueueName=queue_name)["QueueUrl"])
    return q.send_message(MessageBody=json.dumps(message))
