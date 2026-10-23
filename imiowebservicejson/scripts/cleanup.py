# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from datetime import timedelta
from imio.dataexchange.db import DeclarativeBase
from imio.dataexchange.db import temporary_session
from imio.dataexchange.db.mappers.file import File
from sqlalchemy import engine_from_config
from imiowebservicejson import utils

import argparse
import logging
import os
import sqlalchemy as sa

logger = logging.getLogger("imio.webservice.json")
logger.setLevel(logging.DEBUG)

channel = logging.StreamHandler()
channel.setLevel(logging.DEBUG)
logger.addHandler(channel)


class FileCleaner(object):
    def __init__(self, config):
        self.config = config

    def clean(self, keep_days):
        """
        Remove all files that are older than the number of days that we want to keep
        """
        min_date = utils.now() - timedelta(days=keep_days)
        session = self.get_session()
        query = session.query(File).filter(
            sa.and_(
                File.date < min_date,
                File.filepath != None,
                sa.or_(File.update_date == None, File.update_date < min_date),
            )
        )
        counter = 0
        for record in query.all():
            self.remove_file(record.filepath)
            self.update_record(record)
            session.add(record)
            counter += 1
            if counter >= 100:
                session.commit()
        if counter > 0:
            session.commit()

    def remove_file(self, filepath):
        if os.path.exists(filepath):
            logger.info(u"Remove file: {0}".format(filepath))
            os.remove(filepath)

    def update_record(self, record):
        record.filepath = None

    def get_session(self):
        engine = engine_from_config(self.config, prefix="sqlalchemy.")
        session = temporary_session(engine)
        DeclarativeBase.metadata.bind = engine
        return session


def main():
    parser = argparse.ArgumentParser(description=u"Handle requests")
    parser.add_argument("config_uri", type=str)
    parser.add_argument("keep_days", type=int)

    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config_uri)

    FileCleaner(config._sections.get("app:main")).clean(args.keep_days)
