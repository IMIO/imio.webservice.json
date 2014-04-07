# -*- coding: utf-8 -*-
from datetime import datetime
from warlock.model import Model

from zope.interface import implements
from pyramid.events import subscriber

from ..event import ValidatorEvent
from ..exception import ValidationError
from ..interfaces import ITestSchema

UID = -1


def get_id():
    global UID
    UID += 1
    return UID


class BaseJSONObject(Model):

    def __init__(self, schema, *args, **kwargs):
        self.__dict__['schema'] = schema
        Model.__init__(self, *args, **kwargs)


class BaseModel(object):

    def __init__(self, *args, **kwargs):
        self.json_object = BaseJSONObject(self.schema, *args, **kwargs)

    def __getattr__(self, key):
        try:
            return self.__getattribute__(key)
        except AttributeError:
            return getattr(self.json_object, key)


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
