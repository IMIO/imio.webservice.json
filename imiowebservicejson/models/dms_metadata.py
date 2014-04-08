# -*- coding: utf-8 -*-
import os
from datetime import datetime

from zope.interface import implements
from pyramid.events import subscriber

from .base import BaseModel
from .base import get_id
from ..event import ValidatorEvent
from ..exception import ValidationError
from ..interfaces import IDMSMetadata
from ..mappers.file import File


class DMSMetadata(BaseModel):
    implements(IDMSMetadata)

    @property
    def uid(self):
        if hasattr(self, '_uid') is False:
            self._uid = get_id()
        return self._uid

    @property
    def filepath(self):
        return os.path.join(os.environ.get('GED_LOG_PATH', '/tmp'),
                            '%s.json' % self.uid)


@subscriber(ValidatorEvent, implement=IDMSMetadata)
def scan_date_validation(event):
    try:
        datetime.strptime(event.context.scan_date, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("The value for the field 'scan_date' is invalid")


@subscriber(ValidatorEvent, implement=IDMSMetadata)
def scan_hour_validation(event):
    try:
        datetime.strptime(event.context.scan_hour, '%H:%M:%S')
    except ValueError:
        raise ValidationError("The value for the field 'scan_hour' is invalid")


@subscriber(ValidatorEvent, implement=IDMSMetadata)
def external_id(event):
    external_id = event.context.external_id
    if File.exists(user='test', external_id=external_id) is True:
        raise ValidationError("The value for the field 'external_id' "
                              "already exist")
