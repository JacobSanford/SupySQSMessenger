from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
import json
import SQSSettings

def init_sqs():
    sqs_conn = SQSConnection(
        SQSSettings.aws_access_key,
        SQSSettings.aws_secret_key
    )
    sqs_queue = sqs_conn.create_queue(
        SQSSettings.sqs_queue_name
    )
    return sqs_queue


m = Message()

message_body = json.dumps({
                           'message' : 'Test message wooooooooot',
                           'dsid' : '',
                           'language' : 'eng'
                           })

m.set_body(message_body)
init_sqs().write(m)
