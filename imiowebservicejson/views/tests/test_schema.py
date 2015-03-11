# -*- coding: utf-8 -*-

from mock import Mock
from pyramid import security

from imiowebservicejson.views import schema
from imiowebservicejson.views.tests.base import ViewTestCase


class TestsViewsSchema(ViewTestCase):
    views = schema

    def test_schema_request(self):
        security.unauthenticated_userid = Mock(return_value=u'testuser')
        request = self._request
        request.matchdict = {'name': 'dms_metadata',
                             'version': '1.0'}
        self._view_test('schema', 'schema_request', request)

    def test_schema_request_error(self):
        security.unauthenticated_userid = Mock(return_value=u'testuser')
        request = self._request
        request.matchdict = {'name': 'dms_metadata',
                             'version': '0.1'}
        self._view_test('schema', 'schema_request_error', request)
