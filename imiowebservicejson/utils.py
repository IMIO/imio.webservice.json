# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.exc import StatementError


def now():
    return datetime.now()


def has_request_cache(record, ignore_cache=False):
    """Verify if there is a cached response for the given record"""
    if record:
        if not record.expiration_date:
            return True
        if ignore_cache is True:
            return False
        if record.expiration_date and record.expiration_date > now():
            return True
    return False


def test_temporary_session(session):
    """
    Verify if the connection attached to the session is stil open.
    This avoid an error when the connection was closed by database.
    """
    try:
        session.execute("select pk from router limit 1")
    except (OperationalError, InvalidRequestError, StatementError):
        session.rollback()
