# -*- coding: utf-8 -*-
from zope.interface import implementer

from imiowebservicejson.interfaces import IValidatorEvent


@implementer(IValidatorEvent)
class ValidatorEvent(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
