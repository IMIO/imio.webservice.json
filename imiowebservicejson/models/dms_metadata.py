# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import desc

from zope.interface import implements
from pyramid.events import subscriber
from pyramid import security

from imio.dataexchange.db.mappers.file import File

from imiowebservicejson.event import ValidatorEvent
from imiowebservicejson.exception import ValidationError
from imiowebservicejson.interfaces import IDMSMetadata
from imiowebservicejson.models.base import BaseModel


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
        raise ValidationError(
            u'SCAN_DATE_INVALID',
            u"The value for the field 'scan_date' is invalid",
        )


@subscriber(ValidatorEvent, implement=IDMSMetadata)
def scan_hour_validation(event):
    try:
        datetime.strptime(event.context.scan_hour, '%H:%M:%S')
    except ValueError:
        raise ValidationError(
            u'SCAN_HOUR_INVALID',
            u"The value for the field 'scan_hour' is invalid",
        )


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
        raise ValidationError(
            u'EXTERNAL_ID_DUPLICATE',
            u"The value for the field 'external_id' already exist",
        )


@subscriber(ValidatorEvent, implement=IDMSMetadata, version='>=1.2')
def external_id_validation(event):
    if event.context.external_id[:7] != event.context.client_id:
        raise ValidationError(
            u'INVALID_EXTERNAL_ID',
            u"The value for the field 'external_id' is invalid",
        )
