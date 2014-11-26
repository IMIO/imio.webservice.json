# -*- coding: utf-8 -*-

from imio.amqp import BaseSingleMessagePublisher
from imio.amqp import BaseSingleMessageConsumer


class SinglePublisher(BaseSingleMessagePublisher):
    logger_name = 'request_notifier'
    log_file = 'request_notifier.log'

    def get_routing_key(self, message):
        return message.client_id


class Request(object):

    def __init__(self, type, parameters, client_id, uid):
        self.type = type
        self.parameters = parameters
        self.client_id = client_id
        self.uid = uid


class SingleConsumer(BaseSingleMessageConsumer):
    logger_name = 'request_notifier'
    log_file = 'request_notifier.log'
    exchange = 'ws.connection'
