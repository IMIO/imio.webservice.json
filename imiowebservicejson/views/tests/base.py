# encoding: utf-8

from imio.dataexchange.db import DBSession
from imio.dataexchange.db.mappers.file_type import FileType
from imiowebservicejson.fileupload import FileUpload
from mock import Mock
from pyramid import security
from pyramid import testing

import json
import unittest


class ViewTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.config = testing.setUp()
        self._unauthenticated_userid = security.unauthenticated_userid
        self._save_tmpfile = FileUpload.save_tmpfile
        self._move = FileUpload.move
        self._save_reference = FileUpload.save_reference
        DBSession.add(FileType(id="COUR_E", description="description"))
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
        settings = {"traceback.debug": True}
        request.registry = type(
            "registry",
            (object,),
            {"settings": settings, "notify": Mock(return_value=None)},
        )()
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
                    "pattern": "^.+$",
                }
            },
            "required": ["id"],
        }

    def _view_test(self, viewname, json_name, request, **out_kwargs):
        import os

        json_path = os.path.join(os.path.dirname(__file__), "json", json_name)
        in_json = open(os.path.join(json_path, "in.json")).read().strip()
        out_json = open(os.path.join(json_path, "out.json")).read().strip()
        request.json = in_json
        request.json_body = json.loads(in_json)

        view = getattr(self.views, viewname)
        result = view(request)

        in_json = json.loads(in_json)
        out_json = json.loads(out_json)
        for key, value in out_kwargs.items():
            out_json[key] = value
        self.assertEqual(out_json, result)

    def _get_last_file_id(self):
        return DBSession.execute("select currval('file_id_seq')").fetchone()[0]
