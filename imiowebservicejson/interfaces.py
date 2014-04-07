# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IValidatorEvent(Interface):
    context = Attribute('The object to validate')


class ITestSchema(Interface):
    pass
