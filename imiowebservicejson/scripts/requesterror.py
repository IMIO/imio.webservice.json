# -*- coding: utf-8 -*-

from configparser import ConfigParser
from imio.amqp import BaseConsumer
from imiowebservicejson.request import SinglePublisher
from pika.exceptions import AMQPConnectionError

import argparse
import time


class RequestError(BaseConsumer):
    logger_name = "request_error"
    log_file = None
    exchange = "ws.request"
    queue = "ws.request.error"
    routing_key = "request.error"

    def start(self, wait_duration=2):
        self.wait_duration = wait_duration
        super(RequestError, self).start()

    def treat_message(self, message):
        time.sleep(self.wait_duration)
        publisher = SinglePublisher(self._url)
        if message.type == "GET":
            queue_key = "read"
        else:
            queue_key = "write"
        publisher.setup_queue(
            "ws.request.{0}".format(queue_key), "request.{0}".format(queue_key)
        )
        publisher.add_message(message)
        publisher.start()


def generate_consumer(url):
    connection_parameters = "connection_attempts=3&heartbeat_interval=3600"
    consumer = RequestError("{0}/%2Fwebservice?{1}".format(url, connection_parameters))
    consumer.setup_queue("ws.request.error", "request.error")
    return consumer


def main():
    parser = argparse.ArgumentParser(description=u"Handle requests")
    parser.add_argument("config_uri", type=str)

    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config_uri)

    url = config.get("app:main", "rabbitmq.url")
    wait_duration = config.get("app:main", "handler.error.wait")
    while True:
        try:
            consumer = generate_consumer(url)
            consumer.start(wait_duration=int(wait_duration))
        except AMQPConnectionError:
            if consumer._connection:
                try:
                    consumer.stop()
                except AttributeError:
                    # This error happen when RabbitMQ is not ready yet
                    pass
            time.sleep(5)
        except KeyboardInterrupt:
            consumer.stop()
            break
