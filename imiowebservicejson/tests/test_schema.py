# -*- coding: utf-8 -*-

import os.path
import unittest
from mock import Mock

from ..schema import get_schemas


class TestSchema(unittest.TestCase):
    def setUp(self):
        self._dirname = os.path.dirname
        current_dir = os.path.dirname(__file__)
        os.path.dirname = Mock(return_value=current_dir)

    def tearDown(self):
        os.path.dirname = self._dirname

    def test_get_schemas(self):
        input, output = get_schemas("test", "1.0")
        self.assertEqual("test", input["name"])
        self.assertEqual("test", output["name"])
        self.assertEqual("1.0", input["version"])
        self.assertEqual("1.0", output["version"])
        input_properties = [u"id", u"type", u"date"]
        self.assertEqual(sorted(input_properties), sorted(input["properties"].keys()))
        output_properties = [u"success", u"message", u"error"]
        self.assertEqual(sorted(output_properties), sorted(output["properties"].keys()))

    def test_get_schemas_missing(self):
        result = get_schemas("test", "1.x")
        self.assertEqual((None, None), result)
        result = get_schemas("foo", "1.0")
        self.assertEqual((None, None), result)
