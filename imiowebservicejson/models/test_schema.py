# -*- coding: utf-8 -*-
from datetime import datetime

from zope.interface import implements
from pyramid.events import subscriber

from .base import BaseModel
from .base import get_id
from ..event import ValidatorEvent
from ..exception import ValidationError
from ..interfaces import ITestSchema


class TestSchema(BaseModel):
    implements(ITestSchema)

    @property
    def uid(self):
        if hasattr(self, '_uid') is False:
            self._uid = get_id()
        return self._uid

    @property
    def filepath(self):
        return "/home/vagrant/json/%s.json" % self.uid

    @property
    def date(self):
        return datetime.strptime(self.json_object.date, '%Y-%m-%dT%H:%M:%S')


@subscriber(ValidatorEvent, implement=ITestSchema)
def validate_date(event):
    try:
        event.context.date
    except ValueError:
        raise ValidationError("the value 'date' is invalid")


@subscriber(ValidatorEvent, implement=ITestSchema, version=(">= 1.1", "< 2.0"))
def validate_info(event):
    if event.context.info == 'test':
        raise ValidationError(u"Value test is invalid")
