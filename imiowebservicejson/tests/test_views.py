# -*- coding: utf-8 -*-

import json
import unittest
from jsonschema import ValidationError
from mock import Mock

from pyramid import security
from pyramid import testing

from imio.dataexchange.db import DBSession
from imio.dataexchange.db.mappers.file import File
from imio.dataexchange.db.mappers.file_type import FileType

from imiowebservicejson import views
from imiowebservicejson.fileupload import FileUpload


class TestViews(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.config = testing.setUp()
        self._unauthenticated_userid = security.unauthenticated_userid
        self._save_tmpfile = FileUpload.save_tmpfile
        self._move = FileUpload.move
        self._save_reference = FileUpload.save_reference
        DBSession.add(FileType(id='FACT', description='description'))
        DBSession.flush()

    def tearDown(self):
        DBSession.rollback()
        testing.tearDown()
        security.unauthenticated_userid = self._unauthenticated_userid
        FileUpload.save_tmpfile = self._save_tmpfile
        FileUpload.move = self._move
        FileUpload.save_reference = self._save_reference

    @property
    def _request(self):
        request = testing.DummyRequest()
        settings = {'traceback.debug': True}
        request.registry = type('registry', (object, ),
                                {'settings': settings,
                                 'notify': Mock(return_value=None)})()
        return request

    @property
    def _json_schema(self):
        return {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "Json validation test schema",
            "description": "Test schema",
            "type": "object",
            "properties": {
                "id": {
                    "description": "The unique id",
                    "type": "string",
                    "pattern": "^.+$"
                }
            },
            "required": ["id"]
        }

    def _view_test(self, viewname, json_name, request, **out_kwargs):
        import os
        json_path = os.path.join(os.path.dirname(__file__), 'json', json_name)
        in_json = open(os.path.join(json_path, 'in.json')).read().strip()
        out_json = open(os.path.join(json_path, 'out.json')).read().strip()
        request.json = in_json
        request.json_body = json.loads(in_json)

        view = getattr(views, viewname)
        result = view(request)

        in_json = json.loads(in_json)
        out_json = json.loads(out_json)
        for key, value in out_kwargs.items():
            out_json[key] = value
        self.assertEqual(out_json, result)

    def _get_last_file_id(self):
        return DBSession.execute("select currval('file_id_seq')").fetchone()[0]

    def test_failure(self):
        self.assertEqual({"success": False, "message": "FOO"},
                         views.failure("FOO"))
        self.assertEqual({"success": False, "message": "FOO", "error": "BAR"},
                         views.failure("FOO", error="BAR"))

    def test_validate_json_schema(self):
        input_json = {'id': 'T001'}
        schema = self._json_schema
        self.assertIsNone(views.validate_json_schema(input_json, schema))

    def test_validate_json_schema_error(self):
        input_json = {'id': 1}
        schema = self._json_schema
        self.assertEqual("Validation error on 'id': 1 is not of type 'string'",
                         views.validate_json_schema(input_json, schema))

    def test_validate_object(self):
        request = self._request
        request.registry.notify = Mock(return_value=None)
        self.assertIsNone(views.validate_object(request, None))
        request.registry.notify = Mock(side_effect=ValidationError('FOO'))
        self.assertEqual('FOO', views.validate_object(request, None))

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

    def test_dms_metadata_basic(self):
        security.unauthenticated_userid = Mock(return_value=u'testuser')
        request = self._request
        request.matchdict = {'version': '1.0'}
        file_id = self._get_last_file_id() + 1
        self._view_test('dms_metadata', 'dms_metadata_basic', request,
                        id=file_id)
        data = File.first(id=file_id)
        self.assertEqual('testuser', data.user)
        self.assertEqual('CH-00004', data.external_id)

    def test_dms_metadata_update(self):
        data = File(id=1,
                    external_id='CH-00001',
                    client_id='CH',
                    type='FACT',
                    version=1,
                    user='testuser',
                    file_metadata=json.dumps({'filesize': 6}))
        data.insert(flush=True)
        security.unauthenticated_userid = Mock(return_value=u'testuser')
        request = self._request
        request.matchdict = {'version': '1.0'}
        self._view_test('dms_metadata', 'dms_metadata_update', request)
        data = File.first(id=1)
        self.assertIsNotNone(data.update_date)
        self.assertEqual(3030, json.loads(data.file_metadata).get('filesize'))

    def test_dms_metadata_new_version(self):
        data = File(id=1,
                    external_id='CH-00002',
                    client_id='CH',
                    type='FACT',
                    version=1,
                    user='testuser',
                    filepath='/tmp/test.txt',
                    file_metadata=json.dumps({'filesize': 6}))
        data.insert(flush=True)
        security.unauthenticated_userid = Mock(return_value=u'testuser')
        request = self._request
        request.matchdict = {'version': '1.0'}
        file_id = self._get_last_file_id() + 1
        self._view_test('dms_metadata', 'dms_metadata_new_version', request,
                        id=file_id)
        data = File.first(id=file_id)
        self.assertEqual('CH-00002', data.external_id)
        self.assertEqual(2, data.version)
        self.assertEqual(2, File.count(external_id='CH-00002'))

    def test_file(self):
        FileUpload.save_tmpfile = Mock(return_value=None)
        FileUpload.move = Mock(return_value=None)
        FileUpload.save_reference = Mock(return_value=None)
        request = self._request
        request.POST = {'filedata': None}
        result = views.file(request)
        self.assertEqual('File uploaded successfully', result['message'])
        self.assertTrue(result['success'])

    def test_exception_handler(self):
        request = self._request
        result = views.file(request)
        self.assertFalse(result['success'])
        self.assertEqual('An error occured during the process',
                         result['message'])
        self.assertEqual("'filedata'", result['error'])
