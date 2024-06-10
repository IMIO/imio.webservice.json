# -*- coding: utf-8 -*-

from configparser import ConfigParser
from imio.amqp import BasePublisher
from imio.dataexchange.core.document import create_document
from imio.dataexchange.db import DBSession
from imio.dataexchange.db import DeclarativeBase
from imio.dataexchange.db.mappers.file import File
from pika.exceptions import AMQPConnectionError
from sqlalchemy import engine_from_config

import argparse
import time


class DocumentPublisher(BasePublisher):
    logger_name = "document_notifier"
    log_file = None

    def add_messages(self):
        query = File.query(amqp_status=False, order_by=["id"])
        query = query.filter(File.filepath != None)
        query = query.limit(100)
        return query.all()

    def transform_message(self, message):
        return create_document(message)

    def mark_message(self, message):
        message.amqp_status = True
        message.update(commit=True)

    def get_routing_key(self, message):
        return message.type


def generate_publisher(url):
    publisher = DocumentPublisher(
        "{0}/%2Fwebservice?connection_attempts=3&" "heartbeat_interval=3600".format(url)
    )
    publisher.setup_queue("dms.deliberation", "DELIB")
    publisher.setup_queue("dms.incomingmail", "COUR_E")
    publisher.setup_queue("dms.outgoingmail", "COUR_S")
    publisher.setup_queue("dms.outgoinggeneratedmail", "COUR_S_GEN")
    publisher.setup_queue("dms.incoming.email", "EMAIL_E")
    return publisher


def main():
    parser = argparse.ArgumentParser(description=u"Publish the documents in queue")
    parser.add_argument("config_uri", type=str)

    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config_uri)

    engine = engine_from_config(config._sections.get("app:main"), prefix="sqlalchemy.")
    # Remove the transaction manager
    del DBSession.session_factory.kw["extension"]
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.bind = engine

    url = config.get("app:main", "rabbitmq.url")
    while True:
        try:
            publisher = generate_publisher(url)
            publisher.start()
        except AMQPConnectionError:
            if publisher._connection:
                try:
                    publisher.stop()
                except AttributeError:
                    # This error happen when RabbitMQ is not ready yet
                    pass
            time.sleep(20)
        except KeyboardInterrupt:
            publisher.stop()
            break
