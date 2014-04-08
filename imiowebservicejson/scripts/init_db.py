# -*- coding: utf-8 -*-
import argparse

from pyramid.paster import bootstrap

from ..db import DeclarativeBase
from ..mappers.file import File
File  # Pyflakes fix


def main():
    parser = argparse.ArgumentParser(description=u"Initialize the database")
    parser.add_argument('config_uri', type=str)

    args = parser.parse_args()
    bootstrap(args.config_uri)
    DeclarativeBase.metadata.create_all()
