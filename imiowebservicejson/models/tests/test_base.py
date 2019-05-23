# -*- coding: utf-8 -*-

import unittest
from warlock import model_factory

from imiowebservicejson.models.base import BaseModel


class TestBase(unittest.TestCase):
    @property
    def _test_schema(self):
        return {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "test schema",
            "description": "Test schema",
            "type": "object",
            "name": "test",
            "version": "0.1",
            "properties": {
                "id": {
                    "description": "The unique id",
                    "type": "string",
                    "pattern": "^.+$",
                },
                "type": {
                    "description": "The type of the document",
                    "enum": ["FOO", "BAR"],
                },
            },
            "required": ["id", "type"],
        }

    @property
    def _test_values(self):
        return {"id": "0001", "type": "FOO"}

    def test_BaseModel(self):
        model_class = model_factory(self._test_schema, BaseModel)
        model = model_class(**self._test_values)
        model.test = "foo"

        self.assertEqual("FOO", model.type)
        self.assertEqual("0001", model.id)

    def test_BaseModel_validation_error(self):
        model_class = model_factory(self._test_schema, BaseModel)
        values = self._test_values
        values["type"] = "FO"
        self.assertRaises(ValueError, model_class, **values)

    def test_BaseModel_getattr(self):
        model_class = model_factory(self._test_schema, BaseModel)
        model_class.test = "FOO"
        model = model_class(**self._test_values)
        self.assertEqual("FOO", model.test)
        self.assertRaises(AttributeError, getattr, model.json_object, "test")

    def test_BaseModel_setattr(self):
        model_class = model_factory(self._test_schema, BaseModel)
        model = model_class(**self._test_values)
        self.assertRaises(AttributeError, getattr, model, "test")
        model.test = "FOO"
        self.assertEqual("FOO", model.test)
        self.assertRaises(AttributeError, getattr, model.json_object, "test")

    def test_BaseModel_setattr_json(self):
        model_class = model_factory(self._test_schema, BaseModel)
        model = model_class(**self._test_values)
        self.assertEqual("FOO", model.json_object.type)
        model.type = "BAR"
        self.assertEqual("BAR", model.json_object.type)
