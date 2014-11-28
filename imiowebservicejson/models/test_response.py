# -*- coding: utf-8 -*-

from zope.interface import implements

from imiowebservicejson.interfaces import ITestResponse
from imiowebservicejson.models.base import BaseModel


class TestResponse(BaseModel):
    implements(ITestResponse)
