# -*- coding: utf-8 -*-
from zope.interface import implements

from imiowebservicejson.interfaces import IValidatorEvent


class ValidatorEvent(object):
    implements(IValidatorEvent)

    def __init__(self, request, context):
        self.request = request
        self.context = context
