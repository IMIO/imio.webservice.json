# -*- coding: utf-8 -*-
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
DeclarativeBase = declarative_base()


class MapperBase(object):

    @classmethod
    def _build_filter(cls, operator=and_, **kwargs):
        filters = []
        for key, value in kwargs.items():
            column = getattr(cls, key)
            filters.append(column == value)
        return operator(*filters)

    def insert(self, flush=False):
        DBSession.add(self)
        if flush is True:
            DBSession.flush()

    update = insert

    @classmethod
    def exists(cls, **kwargs):
        return DBSession.query(exists().where(cls._build_filter(**kwargs))).scalar()

    @classmethod
    def first(cls, options=[], order_by=[], **kwargs):
        query = DBSession.query(cls)
        query = query.options(options)
        if order_by:
            if isinstance(order_by, list):
                query = query.order_by(*order_by)
            else:
                query = query.order_by(order_by)
        return query.filter(cls._build_filter(**kwargs)).first()
