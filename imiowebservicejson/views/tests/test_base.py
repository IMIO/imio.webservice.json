# -*- coding: utf-8 -*-

from imiowebservicejson.views import base
from imiowebservicejson.views.tests.base import ViewTestCase
from jsonschema import ValidationError
from mock import Mock


class TestViewsBase(ViewTestCase):
    def test_failure_basic(self):
        error_response = {
            "success": False,
            "message": "FOO",
            "error_code": "INTERNAL_ERROR",
        }
        self.assertEqual(error_response, base.failure("FOO"))

    def test_failure_with_error(self):
        error_response = {
            "success": False,
            "message": "FOO",
            "error_code": "INTERNAL_ERROR",
            "error": "BAR",
        }
        self.assertEqual(error_response, base.failure("FOO", error="BAR"))

    def test_failure_with_error_code(self):
        error_response = {"success": False, "message": "FOO", "error_code": "BAR"}
        self.assertEqual(error_response, base.failure("FOO", error_code="BAR"))

    def test_validate_json_schema(self):
        input_json = {"id": "T001"}
        schema = self._json_schema
        self.assertIsNone(base.validate_json_schema(input_json, schema))

    def test_validate_json_schema_error(self):
        input_json = {"id": 1}
        schema = self._json_schema
        self.assertEqual(
            "Validation error on 'id': 1 is not of type 'string'",
            base.validate_json_schema(input_json, schema),
        )

    def test_validate_object(self):
        request = self._request()
        request.registry.notify = Mock(return_value=None)
        self.assertIsNone(base.validate_object(request, None))
        request.registry.notify = Mock(side_effect=ValidationError("FOO"))
        error = base.validate_object(request, None)
        self.assertEqual("FOO", str(error))
