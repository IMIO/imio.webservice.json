# -*- coding: utf-8 -*-

import unittest
from mock import Mock
from warlock import model_factory

from pyramid import security

from imio.dataexchange.db.mappers.file import File

from imiowebservicejson.exception import ValidationError
from imiowebservicejson.schema import get_schemas
from imiowebservicejson.models import dms_metadata


class TestDMSMetadata(unittest.TestCase):

    def setUp(self):
        self._file_first = File.first
        self._unauthenticated_userid = security.unauthenticated_userid

    def tearDown(self):
        File.first = self._file_first
        security.unauthenticated_userid = self._unauthenticated_userid

    @property
    def _schema(self):
        return get_schemas('dms_metadata', '1.0')[0]

    @property
    def _test_values(self):
        return {
            "external_id": "ID-001",
            "type": "FACT",
            "client_id": "CH",
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
        values['update'] = True
        model = self._get_model(values)
        self.assertEqual(True, model.update_flag)

    def test_update_flag_default(self):
        model = self._get_model(self._test_values)
        self.assertEqual(False, model.update_flag)

    def test_scan_date_validation(self):
        model = self._get_model(self._test_values)
        event = type('event', (object, ), {'context': model})()
        self.assertIsNone(dms_metadata.scan_date_validation(event))

    def test_scan_date_validation_error(self):
        model = self._get_model(self._test_values)
        model.scan_date = '2014-02-31'
        event = type('event', (object, ), {'context': model})()
        self.assertRaises(ValidationError,
                          dms_metadata.scan_date_validation, event)

    def test_scan_hour_validation(self):
        model = self._get_model(self._test_values)
        event = type('event', (object, ), {'context': model})()
        self.assertIsNone(dms_metadata.scan_hour_validation(event))

    def test_scan_hour_validation_error(self):
        model = self._get_model(self._test_values)
        model.scan_hour = '25:00:00'
        event = type('event', (object, ), {'context': model})()
        self.assertRaises(ValidationError,
                          dms_metadata.scan_hour_validation, event)

    def test_unicity_validation(self):
        File.first = Mock(return_value=None)
        security.unauthenticated_userid = Mock(return_value='testuser')
        model = self._get_model(self._test_values)
        event = type('event', (object, ), {'context': model, 'request': {}})()
        self.assertIsNone(dms_metadata.unicity_validation(event))

    def test_unicity_validation_update(self):
        model = self._get_model(self._test_values)
        model.update = True
        event = type('event', (object, ), {'context': model})()
        self.assertIsNone(dms_metadata.unicity_validation(event))

    def test_unicity_validation_existing_metadata(self):
        # With file
        file_data = type('file', (object, ), {'filepath': 'test'})()
        File.first = Mock(return_value=file_data)
        security.unauthenticated_userid = Mock(return_value='testuser')
        model = self._get_model(self._test_values)
        event = type('event', (object, ), {'context': model, 'request': {}})()
        self.assertRaises(ValidationError, dms_metadata.unicity_validation,
                          event)

        # Without file
        file_data.filepath = None
        File.first = Mock(return_value=file_data)
        security.unauthenticated_userid = Mock(return_value='testuser')
        model = self._get_model(self._test_values)
        event = type('event', (object, ), {'context': model, 'request': {}})()
        self.assertIsNone(dms_metadata.unicity_validation(event))
