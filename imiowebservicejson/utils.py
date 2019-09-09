# -*- coding: utf-8 -*-

from datetime import datetime


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
