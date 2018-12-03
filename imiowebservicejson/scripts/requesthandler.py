# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from sqlalchemy import engine_from_config
from imio.dataexchange.db.mappers.request import Request
from imio.dataexchange.db.mappers.router import Router
from imio.dataexchange.db import DeclarativeBase
from imio.dataexchange.db import temporary_session
from imio.amqp import BaseConsumer

import argparse
import requests
import json
import sqlalchemy as sa


class RequestHandler(BaseConsumer):
    logger_name = 'request_handler'
    log_file = 'requesthandler.log'
    exchange = 'ws.request'
    queue = 'ws.request'
    routing_key = 'request'

    def start(self, db_config):
        self.db_config = db_config
        super(RequestHandler, self).start()

    def get_url(self, message, session):
        """ Get the routed url for the given message """
        route = session.query(Router.url).filter(sa.and_(
            Router.client_id == message.client_id,
            Router.application_id == message.application_id,
        )).first()
        # XXX Handle missing route
        base_url = route.url
        if base_url.endswith(u'/'):
            base_url = base_url[:-1]
        path = message.path
        if not path.startswith(u'/'):
            path = u'/{0}'.format(path)
        return '{0}{1}'.format(base_url, path)

    def make_request(self, message, url):
        """ Make the request to the routed url """
        me = getattr(requests, message.type.lower())
        parameters = {
            'headers': {'Accept': 'application/json'},
            'auth': ('admin', 'admin'),
        }
        if message.type.lower() == 'patch':
            parameters['headers']['Content-Type'] = 'application/json'
            parameters['headers']['Prefer'] = 'return=representation'
            parameters['json'] = message.parameters
        result = me(url, **parameters)
        return result

    def treat_message(self, message):
        session = self.get_session()
        url = self.get_url(message, session)
        try:
            result = self.make_request(message, url)
        except:
            session.close()
        request = session.query(Request).filter(
            Request.uid == message.uid,
        ).first()
        request.response = json.dumps(result.json())
        session.add(request)
        session.commit()
        session.close()

    def get_session(self):
        engine = engine_from_config(self.db_config, prefix='sqlalchemy.')
        session = temporary_session(engine)
        DeclarativeBase.metadata.bind = engine
        return session


def main():
    parser = argparse.ArgumentParser(description=u'Handle requests')
    parser.add_argument('config_uri', type=str)

    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config_uri)

    url = config.get('app:main', 'rabbitmq.url')
    connection_parameters = 'connection_attempts=3&heartbeat_interval=3600'
    consumer = RequestHandler(
        '{0}/%2Fwebservice?{1}'.format(url, connection_parameters)
    )
    consumer.setup_queue('ws.request', 'request')
    try:
        consumer.start(config._sections.get('app:main'))
    except KeyboardInterrupt:
        consumer.stop()
