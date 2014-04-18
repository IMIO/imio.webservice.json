# -*- coding: utf-8 -*-
from warlock.model import Model


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

    def __setattr__(self, key, value):
        if hasattr(self, 'json_object') is True:
            if key in self.json_object.schema.get('properties'):
                setattr(self.json_object, key, value)
        self.__dict__[key] = value
