# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from datetime import timedelta
from imio.amqp import BaseConsumer
from imio.dataexchange.db import DeclarativeBase
from imio.dataexchange.db import temporary_session
from imio.dataexchange.db.mappers.request import Request
from imio.dataexchange.db.mappers.router import Router
from imiowebservicejson import request
from imiowebservicejson import utils
from pika.exceptions import AMQPConnectionError
from sqlalchemy import engine_from_config
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import StatementError

import argparse
import json
import requests
import sqlalchemy as sa
import time


class BaseRequestHandler(BaseConsumer):
    logger_name = "request_handler"
    log_file = None
    exchange = "ws.request"
    queue = None
    routing_key = None

    def start(self, db_config, error_count):
        self.db_config = db_config
        self.error_count = error_count
        super(BaseRequestHandler, self).start()

    def get_url(self, message, session):
        """ Get the routed url for the given message """
        route = (
            session.query(Router.url)
            .filter(
                sa.and_(
                    Router.client_id == message.client_id,
                    Router.application_id == message.application_id,
                )
            )
            .first()
        )
        # XXX Handle missing route
        base_url = route.url
        if base_url.endswith(u"/"):
            base_url = base_url[:-1]
        path = message.path
        if not path.startswith(u"/"):
            path = u"/{0}".format(path)
        return "{0}{1}".format(base_url, path)

    def make_request(self, message, url):
        """ Make the request to the routed url """
        me = getattr(requests, message.type.lower())
        parameters = {
            "headers": {"Accept": "application/json"},
        }
        if message.auth:
            parameters["auth"] = message.auth
        if message.type.lower() in ("patch", "post", "put"):
            parameters["headers"]["Content-Type"] = "application/json"
            parameters["headers"]["Prefer"] = "return=representation"
            parameters["json"] = message.parameters
        result = me(url, **parameters)
        return result

    def get_cache(self, session, internal_uid):
        """Verify and return an already cached response that we should use"""
        query = session.query(Request.response, Request.expiration_date).filter(
            sa.and_(
                Request.internal_uid == internal_uid,
                Request.response != None,
                Request.expiration_date != None,
                Request.expiration_date > utils.now(),
            )
        )
        result = query.order_by(sa.desc(Request.date)).first()
        if result:
            return result.response, result.expiration_date
        return None, None

    def treat_message(self, message):
        session = self.get_session()
        try:
            utils.test_temporary_session(session)
        except (OperationalError, InvalidRequestError, StatementError):
            # Some errors may happen during rollback
            session.remove()
            session = self.get_session()
        record = Request.first(uid=message.uid, session=session)
        if message.ignore_cache is False:
            cached_response, cached_expiration = self.get_cache(
                session, record.internal_uid
            )
            if cached_response:
                record.response = cached_response
                record.expiration_date = cached_expiration
                record.update(session=session, commit=True)
                session.close()
                return

        url = self.get_url(message, session)
        expiration_date = None
        try:
            result = self.make_request(message, url).json()
            expiration_date = utils.now() + timedelta(
                seconds=message.cache_duration
            )
        except Exception as e:
            if message.error_count >= self.error_count:
                result = {"error": str(e)}
            else:
                message.error_count += 1
                publisher = request.SinglePublisher(self._url)
                publisher.setup_queue("ws.request.error", "request.error")
                publisher.add_message(message)
                publisher.start()
                return
        record.response = json.dumps(result)
        record.expiration_date = expiration_date
        record.update(session=session, commit=True)

    def get_session(self):
        # XXX Detect PostgreSQL restart to avoid losing connection
        if not hasattr(self, "_session"):
            engine = engine_from_config(self.db_config, prefix="sqlalchemy.")
            session = temporary_session(engine)
            DeclarativeBase.metadata.bind = engine
            self._session = session
        return self._session


class ReadRequestHandler(BaseRequestHandler):
    queue = "ws.request.read"
    routing_key = "request.read"


class WriteRequestHandler(BaseRequestHandler):
    queue = "ws.request.write"
    routing_key = "request.write"


def generate_consumer(cls, url, queue_key):
    connection_parameters = "connection_attempts=3&heartbeat_interval=3600"
    consumer = cls("{0}/%2Fwebservice?{1}".format(url, connection_parameters))
    consumer.setup_queue(
        "ws.request.{0}".format(queue_key), "request".format(queue_key)
    )
    return consumer


def execute(cls, queue_key):
    parser = argparse.ArgumentParser(description=u"Handle requests")
    parser.add_argument("config_uri", type=str)

    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config_uri)

    url = config.get("app:main", "rabbitmq.url")
    error_count = config.get("app:main", "handler.error.count")
    while True:
        try:
            consumer = generate_consumer(cls, url, queue_key)
            consumer.start(config._sections.get("app:main"), int(error_count))
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


def read_handler():
    execute(ReadRequestHandler, "read")


def write_handler():
    execute(WriteRequestHandler, "write")
