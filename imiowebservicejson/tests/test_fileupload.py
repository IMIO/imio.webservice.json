# -*- coding: utf-8 -*-

import os
import unittest
from io import StringIO

from imio.dataexchange.db import DBSession
from imio.dataexchange.db.mappers.file import File
from imio.dataexchange.db.mappers.file_type import FileType

from imiowebservicejson.event import ValidatorEvent
from imiowebservicejson.exception import ValidationError
from imiowebservicejson.fileupload import FileUpload
from imiowebservicejson.fileupload import get_blob_path
from imiowebservicejson.fileupload import remove_file
from imiowebservicejson.fileupload import validate_file
from imiowebservicejson.fileupload import validate_file_11


class TestFileUpload(unittest.TestCase):
    def setUp(self):
        DBSession.add(FileType(id="COUR_E", description="description"))
        DBSession.flush()
        self._tmp_files = []

    def tearDown(self):
        DBSession.rollback()
        for id in self._tmp_files:
            if os.path.exists("/tmp/%s.txt" % id) is True:
                os.remove("/tmp/%s.txt" % id)

    def _create_tmp_file(self, id="120", content="FOOBAR"):
        self._tmp_files.append(id)
        tmp_file = open("/tmp/%s.txt" % id, "w")
        tmp_file.write(content)
        tmp_file.close()

    def _request(self, id, content):
        uploaded_file = StringIO()
        uploaded_file.write(content)
        post = {
            "filedata": type(
                "filedata", (object,), {"filename": "test.txt", "file": uploaded_file}
            )
        }
        matchdict = {"id": id}
        registry = type(
            "registry", (object,), {"settings": {"dms.storage.path": "./"}}
        )()
        return type(
            "request",
            (object,),
            {"POST": post, "matchdict": matchdict, "registry": registry},
        )()

    def _file(self, id="120", content="FOOBAR"):
        return FileUpload(self._request(id, content))

    def _event(self, version="1.0"):
        context = type("context", (object,), {"version": version})()
        return type("event", (object,), {"context": context})()

    def test_remove_file(self):
        self._create_tmp_file()
        self.assertTrue(os.path.exists("/tmp/120.txt"))
        remove_file("tmp_path", self._file(), None, test=None)
        self.assertFalse(os.path.exists("/tmp/120.txt"))

    def test_remove_file_validatorevent(self):
        self._create_tmp_file()
        event = ValidatorEvent(None, self._file())
        self.assertTrue(os.path.exists("/tmp/120.txt"))
        remove_file("tmp_path", event, None, test=None)
        self.assertFalse(os.path.exists("/tmp/120.txt"))

    def test_id(self):
        self.assertEqual(120, self._file().id)

    def test_filename(self):
        self.assertEqual("120.txt", self._file().filename)

    def test_basepath(self):
        path = get_blob_path(12345678901234)
        self.assertEqual("12/34/56/78/90/12", path)
        path = get_blob_path(3411)
        self.assertEqual("00/00/00/00/00/34", path)
        path = get_blob_path(3567)
        self.assertEqual("00/00/00/00/00/35", path)

    def test_filepath(self):
        self.assertEqual("./00/00/00/00/00/01/120.txt", self._file().filepath)

    def test_tmp_path(self):
        self.assertEqual("/tmp/120.txt", self._file().tmp_path)

    def test_size(self):
        self._create_tmp_file()
        self.assertTrue(os.path.exists(self._file().tmp_path))
        self.assertEqual(6, self._file().size)

    def test_data_cached(self):
        _file = self._file()
        _file._data = "test"
        self.assertEqual("test", _file.data)

    def test_data(self):
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "901890a8e9c8cf6d5a1a542b229febff",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        file_data = self._file().data
        self.assertEqual(120, file_data.id)

    def test_save_tmpfile(self):
        self.assertFalse(os.path.exists(self._file().tmp_path))
        self._file().save_tmpfile()
        self.assertTrue(os.path.exists(self._file().tmp_path))
        self.assertEqual("FOOBAR", open(self._file().tmp_path).read())

    def test_move(self):
        self._create_tmp_file()
        self.assertTrue(os.path.exists(self._file().tmp_path))
        self._file().move()
        self.assertTrue(os.path.exists(self._file().filepath))
        self.assertFalse(os.path.exists(self._file().tmp_path))

    def test_save_reference(self):
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "901890a8e9c8cf6d5a1a542b229febff",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        self._file().save_reference()
        record = File.first(id=120)
        self.assertEqual("./00/00/00/00/00/01/120.txt", record.filepath)

    def test_handle_exception(self):
        self._create_tmp_file()
        file_upload = self._file()
        file_upload._file.file = None
        self.assertTrue(os.path.exists(file_upload.tmp_path))
        self.assertRaises(AttributeError, file_upload.save_tmpfile)
        self.assertFalse(os.path.exists(file_upload.tmp_path))

    def test_validate_file_no_data(self):
        self._create_tmp_file()
        event = ValidatorEvent(None, self._file())
        self.assertRaisesRegex(
            ValidationError, ".*no metadata.*", validate_file, event
        )

    def test_validate_file_already_exist(self):
        self._create_tmp_file()
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
            filepath="/tmp/120.txt",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "95c72a49c488d59f60c022fcfecf4382",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        file_upload = self._file()
        file = open(self._file().filepath, "w")
        file.write("FOOBAR")
        file.close()
        event = ValidatorEvent(self._event(), file_upload)
        self.assertIsNone(validate_file(event))

    def test_validate_file_filesize_mismatch(self):
        self._create_tmp_file()
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 4,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "95c72a49c488d59f60c022fcfecf4382",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file())
        self.assertRaisesRegex(
            ValidationError, ".*filesize does not match.*", validate_file, event
        )

    def test_validate_file_md5_mismatch(self):
        self._create_tmp_file()
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "95c72a49c488d59f60c022fcfecf4382XXX",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file())
        self.assertRaisesRegex(
            ValidationError, ".*MD5 check: difference found.*", validate_file_11, event
        )

    def test_validate_file_md5_uppercase(self):
        self._create_tmp_file()
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "95C72A49C488D59F60C022FCFECF4382",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file())
        validate_file_11(event)

    def test_validate_file(self):
        self._create_tmp_file()
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "95c72a49c488d59f60c022fcfecf4382",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file())
        self.assertIsNone(validate_file_11(event))

    def test_validate_file_update(self):
        self._create_tmp_file()
        record = File(
            id=120,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "95c72a49c488d59f60c022fcfecf4382",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file())
        validate_file_11(event)

        self._create_tmp_file(id="121", content="FOO")
        record = File(
            id=121,
            external_id="CH-0001",
            client_id="CH",
            type="COUR_E",
            version=2,
            user="testuser",
        )
        metadata = {
            "filesize": 3,
            "type": "COUR_E",
            "client_id": "CH",
            "external_id": "CH-0001",
            "filemd5": "901890a8e9c8cf6d5a1a542b229febff",
        }
        record.file_metadata = metadata
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file(id="121", content="FOO"))
        validate_file_11(event)
