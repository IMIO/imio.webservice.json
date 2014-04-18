# -*- coding: utf-8 -*-


def pytest_sessionstart():
    import os
    from paste.deploy.loadwsgi import appconfig
    from sqlalchemy import engine_from_config

    from .db import DBSession
    from .db import DeclarativeBase

    from .mappers.file import File
    File  # Pyflakes fix

    cwd = os.path.dirname(__file__)
    settings = appconfig('config:%s' % os.path.join(cwd, 'test.ini'))
    engine = engine_from_config(settings, 'sqlalchemy.')

    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.bind = engine
    DeclarativeBase.metadata.create_all()  # Create tables

    # Initialize the sequence
    DBSession.execute("select nextval('file_id_seq')").fetchall()

    os.environ['GED_UPLOAD_PATH'] = './'
