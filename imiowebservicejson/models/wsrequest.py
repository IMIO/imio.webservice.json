# -*- coding: utf-8 -*-

from zope.interface import implements

from imiowebservicejson.interfaces import IWSRequest
from imiowebservicejson.models.base import BaseModel


class WSRequest(BaseModel):
    implements(IWSRequest)
