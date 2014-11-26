# -*- coding: utf-8 -*-

from zope.interface import implements

from imiowebservicejson.interfaces import ITestRequest
from imiowebservicejson.models.base import BaseModel


class TestRequest(BaseModel):
    implements(ITestRequest)
