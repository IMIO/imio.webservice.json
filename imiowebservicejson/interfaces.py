# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IValidatorEvent(Interface):
    context = Attribute('The object to validate')


class ITestSchema(Interface):
    """ Marker interface for test_schema json model """


class IDMSMetadata(Interface):
    """ Marker interface for dms_metadata json model """
