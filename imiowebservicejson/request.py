# -*- coding: utf-8 -*-

from imio.amqp import BaseSingleMessagePublisher
from imio.amqp import BaseSingleMessageConsumer


class SinglePublisher(BaseSingleMessagePublisher):
    logger_name = 'request_notifier'
    log_file = 'request_notifier.log'
    exchange = 'ws.request'

    def get_routing_key(self, message):
        return message.client_id


class Request(object):

    def __init__(self, type, parameters, client_id, uid):
        self.type = type
        self.parameters = parameters
        self.client_id = client_id
        self.uid = uid
        self.files = []

    def add_file(self, file):
        self.files.append(file)


class RequestFile(object):

    def __init__(self, uid, metadata):
        self.uid = uid
        self.metadata = metadata


class SingleConsumer(BaseSingleMessageConsumer):
    logger_name = 'request_notifier'
    log_file = 'request_notifier.log'
    exchange = 'ws.response'
