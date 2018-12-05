# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from imio.amqp import BaseConsumer
from imiowebservicejson.request import SinglePublisher

import argparse
import time


class RequestError(BaseConsumer):
    logger_name = 'request_error'
    log_file = 'requesterror.log'
    exchange = 'ws.error'
    queue = 'ws.error'
    routing_key = 'error'

    def start(self, wait_duration=2):
        self.wait_duration = wait_duration
        super(RequestError, self).start()

    def treat_message(self, message):
        time.sleep(self.wait_duration)
        publisher = SinglePublisher(self._url)
        publisher.setup_queue('ws.request', 'request')
        publisher.add_message(message)
        publisher.start()


def main():
    parser = argparse.ArgumentParser(description=u'Handle requests')
    parser.add_argument('config_uri', type=str)

    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config_uri)

    url = config.get('app:main', 'rabbitmq.url')
    wait_duration = config.get('app:main', 'handler.error.wait')
    connection_parameters = 'connection_attempts=3&heartbeat_interval=3600'
    consumer = RequestError(
        '{0}/%2Fwebservice?{1}'.format(url, connection_parameters)
    )
    consumer.setup_queue('ws.error', 'error')
    try:
        consumer.start(wait_duration=int(wait_duration))
    except KeyboardInterrupt:
        consumer.stop()
