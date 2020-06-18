# -*- coding: utf-8 -*-

from imio.dataexchange.db import temporary_session
from sqlalchemy import engine_from_config

_SESSION = {}


def get_session(request):
    if "session" not in _SESSION:
        engine = engine_from_config(request.registry.settings, "sqlalchemy.")
        _SESSION["session"] = temporary_session(engine)
    return _SESSION["session"]
