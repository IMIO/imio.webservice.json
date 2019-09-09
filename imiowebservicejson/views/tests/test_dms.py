# -*- coding: utf-8 -*-
#
from imio.dataexchange.db.mappers.file import File
from imiowebservicejson.fileupload import FileUpload
from imiowebservicejson.views import dms
from imiowebservicejson.views.tests.base import ViewTestCase
from mock import Mock


class TestViewsDMS(ViewTestCase):
    views = dms

    def test_dms_metadata_basic(self):
        request = self._request()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        request.matchdict = {"version": "1.0"}
        file_id = self._get_last_file_id() + 1
        self._view_test("dms_metadata", "dms_metadata_basic", request, id=file_id)
        data = File.first(id=file_id)
        self.assertEqual("testuser", data.user)
        self.assertEqual("010462000000004", data.external_id)

    def test_dms_metadata_update(self):
        data = File(
            id=1,
            external_id="010462000000001",
            client_id="0104620",
            type="COUR_E",
            version=1,
            user="testuser",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "0104620",
            "external_id": "010462000000001",
            "filemd5": "901890a8e9c8cf6d5a1a542b229febff",
        }
        data.file_metadata = metadata
        data.insert(flush=True)
        request = self._request()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        request.matchdict = {"version": "1.0"}
        self._view_test("dms_metadata", "dms_metadata_update", request)
        data = File.first(id=1)
        self.assertIsNotNone(data.update_date)
        self.assertEqual(3030, data.file_metadata.get("filesize"))

    def test_dms_metadata_new_version(self):
        data = File(
            id=1,
            external_id="010462000000002",
            client_id="0104620",
            type="COUR_E",
            version=1,
            user="testuser",
            filepath="/tmp/test.txt",
        )
        metadata = {
            "filesize": 6,
            "type": "COUR_E",
            "client_id": "0104620",
            "external_id": "010462000000002",
            "filemd5": "901890a8e9c8cf6d5a1a542b229febff",
        }
        data.file_metadata = metadata
        data.insert(flush=True)
        request = self._request()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        request.matchdict = {"version": "1.0"}
        file_id = self._get_last_file_id() + 1
        self._view_test("dms_metadata", "dms_metadata_new_version", request, id=file_id)
        data = File.first(id=file_id)
        self.assertEqual("010462000000002", data.external_id)
        self.assertEqual(2, data.version)
        self.assertEqual(2, File.count(external_id="010462000000002"))

    def test_file_upload(self):
        FileUpload.save_tmpfile = Mock(return_value=None)
        FileUpload.move = Mock(return_value=None)
        FileUpload.save_reference = Mock(return_value=None)
        request = self._request()
        request.POST = {"filedata": None}
        result = dms.file_upload(request)
        self.assertEqual("File uploaded successfully", result["message"])
        self.assertTrue(result["success"])

    def test_exception_handler(self):
        request = self._request()
        result = dms.file_upload(request)
        self.assertFalse(result["success"])
        self.assertEqual("An error occured during the process", result["message"])
        self.assertEqual("'filedata'", result["error"])
