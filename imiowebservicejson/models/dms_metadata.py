# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import desc

from zope.interface import implements
from pyramid.events import subscriber
from pyramid import security

from imio.dataexchange.db.mappers.file import File

from .base import BaseModel
from ..event import ValidatorEvent
from ..exception import ValidationError
from ..interfaces import IDMSMetadata


class DMSMetadata(BaseModel):
    implements(IDMSMetadata)

    @property
    def update_flag(self):
        return self.get('update', False)


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
def unicity_validation(event):
    if event.context.update_flag is True:
        return
    userid = security.unauthenticated_userid(event.request)
    external_id = event.context.external_id
    file_data = File.first(user=userid,
                           external_id=external_id,
                           order_by=[desc(File.version)])
    if file_data is not None and file_data.filepath is not None:
        raise ValidationError("The value for the field 'external_id' "
                              "already exist")
