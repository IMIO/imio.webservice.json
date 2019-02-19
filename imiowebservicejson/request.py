# -*- coding: utf-8 -*-

from imio.amqp import BaseSingleMessagePublisher
from imio.amqp import BaseSingleMessageConsumer


class SinglePublisher(BaseSingleMessagePublisher):
    logger_name = 'request_notifier'
    log_file = 'request_notifier.log'
    exchange = 'ws.request'
