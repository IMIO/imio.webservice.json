# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from sqlalchemy import engine_from_config
import argparse

from imiowebservicejson.db import DBSession
from imiowebservicejson.db import DeclarativeBase
from imiowebservicejson.mappers.file import File
from imio.amqp import BasePublisher
from imio.dataexchange.core.document import create_document


class DocumentPublisher(BasePublisher):
    queue = 'dms.document'
    routing_key = 'dms_metadata'
    logger_name = 'document_notifier'
    log_file = 'docnotifier.log'

    def add_messages(self):
        query = File.query(amqp_status=False)
        query = query.filter(File.filepath != None)
        query = query.limit(100)
        return query.all()

    def transform_message(self, message):
        return create_document(message)

    def mark_message(self, message):
        message.amqp_status = True
        message.update(commit=True)


def main():
    parser = argparse.ArgumentParser(description=u"Initialize the database")
    parser.add_argument('config_uri', type=str)

    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config_uri)

    engine = engine_from_config(config._sections.get('app:main'),
                                prefix='sqlalchemy.')
    # Remove the transaction manager
    del DBSession.session_factory.kw['extension']
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.bind = engine

    url = config.get('app:main', 'rabbitmq.url')
    publisher = DocumentPublisher('{0}/%2F?connection_attempts=3&'
                                  'heartbeat_interval=3600'.format(url))
    try:
        publisher.start()
    except KeyboardInterrupt:
        publisher.stop()
