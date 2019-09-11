# -*- coding: utf-8 -*-

from imio.dataexchange.db import temporary_session
from sqlalchemy import engine_from_config


def get_session(request):
    engine = engine_from_config(request.registry.settings, "sqlalchemy.")
    return temporary_session(engine)
