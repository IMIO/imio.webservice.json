# -*- coding: utf-8 -*-
import argparse
import transaction

from pyramid.paster import bootstrap

from imiowebservicejson.mappers.file import File
from imio.document.amqp import BasePublisher
from imio.document.document import create_document


class DocumentPublisher(BasePublisher):
    queue = 'ged.document'
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
        message.update()
        transaction.commit()


def main():
    parser = argparse.ArgumentParser(description=u"Initialize the database")
    parser.add_argument('config_uri', type=str)

    args = parser.parse_args()
    registry = bootstrap(args.config_uri).get('registry')
    url = registry.settings.get('rabbitmq.url')
    publisher = DocumentPublisher('{0}/%2F?connection_attempts=3&'
                                  'heartbeat_interval=3600'.format(url))
    try:
        publisher.start()
    except KeyboardInterrupt:
        publisher.stop()
