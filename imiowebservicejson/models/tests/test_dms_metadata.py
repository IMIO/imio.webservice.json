# -*- coding: utf-8 -*-

from imio.dataexchange.db.mappers.file import File
from imiowebservicejson.exception import ValidationError
from imiowebservicejson.models import dms_metadata
from imiowebservicejson.schema import get_schemas
from mock import Mock
from pyramid import testing
from pyramid.testing import DummyRequest
from warlock import model_factory

import unittest


class TestDMSMetadata(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self._file_first = File.first

    def tearDown(self):
        File.first = self._file_first
        testing.tearDown()

    @property
    def _schema(self):
        return get_schemas("dms_metadata", "1.0")[0]

    @property
    def _test_values(self):
        return {
            "external_id": "010462000000005",
            "type": "COUR_E",
            "client_id": "0104620",
            "scan_date": "2014-01-01",
            "scan_hour": "10:30:25",
            "creator": "testuser",
            "filesize": 5500,
            "filename": "test.pdf",
            "filemd5": "901890a8e9c8cf6d5a1a542b229febff",
        }

    def _get_model(self, values):
        model_class = model_factory(self._schema, dms_metadata.DMSMetadata)
        return model_class(**values)

    def test_update_flag(self):
        values = self._test_values
        values["update"] = True
        model = self._get_model(values)
        self.assertEqual(True, model.update_flag)

    def test_update_flag_default(self):
        model = self._get_model(self._test_values)
        self.assertEqual(False, model.update_flag)

    def test_scan_date_validation(self):
        model = self._get_model(self._test_values)
        event = type("event", (object,), {"context": model})()
        self.assertIsNone(dms_metadata.scan_date_validation(event))

    def test_scan_date_validation_error(self):
        model = self._get_model(self._test_values)
        model.scan_date = "2014-02-31"
        event = type("event", (object,), {"context": model})()
        self.assertRaises(ValidationError, dms_metadata.scan_date_validation, event)

    def test_scan_hour_validation(self):
        model = self._get_model(self._test_values)
        event = type("event", (object,), {"context": model})()
        self.assertIsNone(dms_metadata.scan_hour_validation(event))

    def test_scan_hour_validation_error(self):
        model = self._get_model(self._test_values)
        model.scan_hour = "25:00:00"
        event = type("event", (object,), {"context": model})()
        self.assertRaises(ValidationError, dms_metadata.scan_hour_validation, event)

    def test_unicity_validation(self):
        File.first = Mock(return_value=None)
        request = DummyRequest()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        model = self._get_model(self._test_values)
        event = type("event", (object,), {"context": model, "request": request})()
        self.assertIsNone(dms_metadata.unicity_validation(event))

    def test_unicity_validation_update(self):
        model = self._get_model(self._test_values)
        model.update = True
        event = type("event", (object,), {"context": model})()
        self.assertIsNone(dms_metadata.unicity_validation(event))

    def test_unicity_validation_existing_metadata(self):
        # With file
        file_data = type("file", (object,), {"filepath": "test"})()
        File.first = Mock(return_value=file_data)
        request = DummyRequest()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        model = self._get_model(self._test_values)
        event = type("event", (object,), {"context": model, "request": request})()
        self.assertRaises(ValidationError, dms_metadata.unicity_validation, event)

        # Without file
        file_data.filepath = None
        File.first = Mock(return_value=file_data)
        request = DummyRequest()
        self.config.testing_securitypolicy(userid="testuser", permissive=True)
        model = self._get_model(self._test_values)
        event = type("event", (object,), {"context": model, "request": request})()
        self.assertIsNone(dms_metadata.unicity_validation(event))

    def test_external_id_validation(self):
        model = self._get_model(self._test_values)
        event = type("event", (object,), {"context": model, "request": {}})()
        self.assertIsNone(dms_metadata.external_id_validation(event))

    def test_external_id_validation_error(self):
        values = self._test_values
        values["client_id"] = "FOO"
        model = self._get_model(values)
        event = type("event", (object,), {"context": model, "request": {}})()
        self.assertRaises(ValidationError, dms_metadata.external_id_validation, event)

    def test_client_id_validation(self):
        model = self._get_model(self._test_values)
        event = type("event", (object,), {"context": model, "request": {}})()
        self.assertIsNone(dms_metadata.client_id_validation(event))

    def test_client_id_validation_error(self):
        values = self._test_values
        values["client_id"] = "01Y4620"
        model = self._get_model(values)
        event = type("event", (object,), {"context": model, "request": {}})()
        self.assertRaises(ValidationError, dms_metadata.client_id_validation, event)
