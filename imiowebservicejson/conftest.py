# -*- coding: utf-8 -*-


def pytest_sessionstart():
    from imio.dataexchange.db import DBSession
    from imio.dataexchange.db import DeclarativeBase
    from imio.dataexchange.db.mappers.file import File
    from paste.deploy.loadwsgi import appconfig
    from sqlalchemy import engine_from_config
    from sqlalchemy import text

    import os

    File  # Pyflakes fix

    cwd = os.path.dirname(__file__)
    settings = appconfig("config:%s" % os.path.join(cwd, "test.ini"))
    engine = engine_from_config(settings, "sqlalchemy.")

    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.create_all(bind=engine)  # Create tables

    # Initialize the sequence
    DBSession.execute(text("select nextval('file_id_seq')")).fetchall()

    os.environ["GED_UPLOAD_PATH"] = "./"
