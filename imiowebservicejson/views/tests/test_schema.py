# -*- coding: utf-8 -*-

from imiowebservicejson.views import schema
from imiowebservicejson.views.tests.base import ViewTestCase
from mock import Mock


class TestsViewsSchema(ViewTestCase):
    views = schema

    def test_schema_request(self):
        request = self._request()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        request.matchdict = {"name": "dms_metadata", "version": "1.0"}
        self._view_test("schema", "schema_request", request)

    def test_schema_request_error(self):
        request = self._request()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        request.matchdict = {"name": "dms_metadata", "version": "0.1"}
        self._view_test("schema", "schema_request_error", request)
