# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IValidatorEvent(Interface):
    context = Attribute('The object to validate')


class IFileUpload(Interface):
    """Marker interface for uploaded files"""


class IDMSMetadata(Interface):
    """Marker interface for dms_metadata json model"""


class IWSRequest(Interface):
    """Marker interface for wsrequest json model"""


class IWSResponse(Interface):
    """Marker interface for wsresponse json model"""
