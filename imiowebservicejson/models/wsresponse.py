# -*- coding: utf-8 -*-

from zope.interface import implements

from imiowebservicejson.interfaces import IWSResponse
from imiowebservicejson.models.base import BaseModel


class WSResponse(BaseModel):
    implements(IWSResponse)
