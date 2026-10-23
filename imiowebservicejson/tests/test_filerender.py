# -*- coding: utf-8 -*-

from imio.dataexchange.db import DBSession
from imio.dataexchange.db.mappers.file import File
from imio.dataexchange.db.mappers.file_type import FileType
from imiowebservicejson.filerender import FileRender
from pyramid import testing

import tempfile
import unittest


class TestFileRender(unittest.TestCase):
    def setUp(self):
        DBSession.add(FileType(id="COUR_E", description="description"))
        DBSession.flush()

    def tearDown(self):
        DBSession.rollback()

    def test_render_binary(self):
        content = b"PK\x03\x04\xbc"  # not UTF-8, like an .odt
        with tempfile.NamedTemporaryFile(suffix=".odt") as f:
            f.write(content)
            f.flush()
            File(
                id=120,
                external_id="CH-0001",
                client_id="CH",
                type="COUR_E",
                version=1,
                user="testuser",
                file_metadata={"external_id": "CH-0001", "client_id": "CH"},
                filepath=f.name,
            ).insert(flush=True)
            request = testing.DummyRequest()
            request.matchdict = {"client_id": "CH", "external_id": "CH-0001"}
            response = FileRender(request).render()
            self.assertEqual(content, response.body)
            self.assertEqual("application/vnd.oasis.opendocument.text", response.content_type)
