# -*- coding: utf-8 -*-
import json as jsonmodule

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.schema import UniqueConstraint
#from sqlalchemy.dialects.postgresql import JSON

from ..db import DeclarativeBase
from ..db import MapperBase


class File(DeclarativeBase, MapperBase):
    __tablename__ = u'file'
    __table_args__ = (
        UniqueConstraint(u'external_id', u'version', u'user',
                         name='user_external_id'),
    )

    id = Column(u'id', Integer, primary_key=True, unique=True, nullable=False)

    external_id = Column(u'external_id', Text, nullable=False)

    version = Column('version', Integer, nullable=False)

    date = Column(u'date', DateTime, nullable=False, server_default=func.now())

    update_date = Column(u'update_date', DateTime)

    user = Column(u'user', Text, nullable=False)

    _file_metadata = Column(u'metadata', Text, nullable=False)
    #file_metadata = Column(u'metadata', JSON, nullable=False)

    filepath = Column(u'filepath', Text)

    @property
    def file_metadata(self):
        return jsonmodule.loads(self._file_metadata)

    @file_metadata.setter
    def file_metadata(self, value):
        self._file_metadata = value
