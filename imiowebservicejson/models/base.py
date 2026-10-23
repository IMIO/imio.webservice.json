# -*- coding: utf-8 -*-
from jsonschema.validators import validator_for
from warlock.model import Model


class BaseJSONObject(Model):
    def __init__(self, schema, *args, **kwargs):
        self.__dict__["schema"] = schema
        # warlock 2 validates with the instance that model_factory normally sets
        self.__dict__["validator_instance"] = validator_for(schema)(schema)
        Model.__init__(self, *args, **kwargs)


class BaseModel(object):
    def __init__(self, *args, **kwargs):
        self.json_object = BaseJSONObject(self.schema, *args, **kwargs)

    def __getattr__(self, key):
        # Called before __init__ sets json_object (e.g. by hasattr in __setattr__)
        if key == "json_object":
            raise AttributeError(key)
        return getattr(self.json_object, key)

    def __setattr__(self, key, value):
        if hasattr(self, "json_object") is True:
            if key in self.json_object.schema.get("properties"):
                setattr(self.json_object, key, value)
        self.__dict__[key] = value
