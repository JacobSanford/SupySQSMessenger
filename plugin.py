import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
from supybot.commands import *
from threading import Thread
from boto.sqs.connection import SQSConnection
from boto.sqs.message import RawMessage
import time
import json
import SQSSettings

class SupySQSMessenger(callbacks.Plugin):
    """SupySQSMessenger queries an SQS queue and parrots
    the messages within to specified channels."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(SupySQSMessenger, self)
        self.__parent.__init__(irc)

        self.locked = False
        self.sqs_conn = False
        self.sqs_queue = False
        self.run_agent = True
        self.message_output_queue = []
        self.irc_object = irc

        self.agent_thread = Thread(target=self.sqs_messenger_agent)
        self.agent_thread.setDaemon(True)
        self.agent_thread.start()

    def die(self):
        self.run_agent = False
        self.__parent.die()

    def get_messages(self):
        """Get messages fed from the SQS queue."""
        message_list = self.sqs_queue.get_messages()
        for current_message in message_list:
            self.message_output_queue.append(current_message)

    def output_messages(self):
        """Retrieve, output and parse messages fed from the SQS queue."""
        for current_message in self.message_output_queue:
            try:
                cur_message_string = json.loads(current_message.get_body().replace("\r","\n"))['Message']
            except:
                cur_message_string = current_message.get_body()
            try:
                message_lines = cur_message_string.split('\n')
            except AttributeError:
                message_lines = cur_message_string
            for cur_channel in SQSSettings.sqs_output_channels:
                for cur_line in message_lines:
                    self.irc_object.queueMsg(ircmsgs.privmsg(cur_channel, ''.join([i if ord(i) < 128 else ' ' for i in cur_line])))
            self.sqs_queue.delete_message(current_message)
        self.message_output_queue = []

    def sqs_messenger_agent(self):
        """Check for messages every sleep_time seconds until stopped."""
        try:
            while self.run_agent is True:
                if not self.locked:
                    self.locked = True
                    self.open_sqs()
                    self.get_messages()
                    self.output_messages()
                    self.close_sqs()
                    self.locked = False
                time.sleep(20)
        except:
            pass

    def open_sqs(self):
        self.sqs_conn = SQSConnection(
            SQSSettings.aws_access_key,
            SQSSettings.aws_secret_key
        )
        self.sqs_queue = self.sqs_conn.create_queue(
            SQSSettings.sqs_queue_name
        )
        self.sqs_queue.set_message_class(RawMessage)

    def close_sqs(self):
        self.sqs_conn = False
        self.sqs_queue = False

Class = SupySQSMessenger
