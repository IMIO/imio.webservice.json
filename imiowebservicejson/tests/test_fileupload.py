# -*- coding: utf-8 -*-

import json
import os
import unittest
from StringIO import StringIO

from ..db import DBSession
from ..event import ValidatorEvent
from ..exception import ValidationError
from ..fileupload import FileUpload
from ..fileupload import remove_file
from ..fileupload import validate_file
from ..mappers.file import File


class TestFileUpload(unittest.TestCase):

    def tearDown(self):
        DBSession.rollback()
        if os.path.exists('/tmp/120.txt') is True:
            os.remove('/tmp/120.txt')

    def _create_tmp_file(self):
        tmp_file = open('/tmp/120.txt', 'w')
        tmp_file.write('FOOBAR')
        tmp_file.close()

    @property
    def _request(self):
        uploaded_file = StringIO()
        uploaded_file.write('FOOBAR')
        post = {'filedata': type('filedata', (object, ),
                                 {'filename': 'test.txt',
                                  'file': uploaded_file})}
        matchdict = {'id': '120'}
        return type('request', (object, ), {'POST': post,
                                            'matchdict': matchdict})()

    @property
    def _file(self):
        return FileUpload(self._request)

    def test_remove_file(self):
        self._create_tmp_file()
        self.assertTrue(os.path.exists('/tmp/120.txt'))
        remove_file('tmp_path', self._file, None, test=None)
        self.assertFalse(os.path.exists('/tmp/120.txt'))

    def test_remove_file_validatorevent(self):
        self._create_tmp_file()
        event = ValidatorEvent(None, self._file)
        self.assertTrue(os.path.exists('/tmp/120.txt'))
        remove_file('tmp_path', event, None, test=None)
        self.assertFalse(os.path.exists('/tmp/120.txt'))

    def test_id(self):
        self.assertEqual('120', self._file.id)

    def test_filename(self):
        self.assertEqual('120.txt', self._file.filename)

    def test_filepath(self):
        self.assertEqual('./120.txt', self._file.filepath)

    def test_tmp_path(self):
        self.assertEqual('/tmp/120.txt', self._file.tmp_path)

    def test_size(self):
        self._create_tmp_file()
        self.assertTrue(os.path.exists(self._file.tmp_path))
        self.assertEqual(6, self._file.size)

    def test_data_cached(self):
        _file = self._file
        _file._data = 'test'
        self.assertEqual('test', _file.data)

    def test_data(self):
        record = File(id=120,
                      external_id='CH-0001',
                      version=1,
                      user='testuser')
        record.file_metadata = json.dumps({'filesize': 6})
        record.insert(flush=True)
        file_data = self._file.data
        self.assertEqual(120, file_data.id)

    def test_save_tmpfile(self):
        self.assertFalse(os.path.exists(self._file.tmp_path))
        self._file.save_tmpfile()
        self.assertTrue(os.path.exists(self._file.tmp_path))
        self.assertEqual('FOOBAR', open(self._file.tmp_path).read())

    def test_move(self):
        self._create_tmp_file()
        self.assertTrue(os.path.exists(self._file.tmp_path))
        self._file.move()
        self.assertTrue(os.path.exists(self._file.filepath))
        self.assertFalse(os.path.exists(self._file.tmp_path))

    def test_save_reference(self):
        record = File(id=120,
                      external_id='CH-0001',
                      version=1,
                      user='testuser',
                      file_metadata=json.dumps({'filesize': 6}))
        record.insert(flush=True)
        self._file.save_reference()
        record = File.first(id=120)
        self.assertEqual('./120.txt', record.filepath)

    def test_handle_exception(self):
        self._create_tmp_file()
        file_upload = self._file
        file_upload._file.file = None
        self.assertTrue(os.path.exists(file_upload.tmp_path))
        self.assertRaises(AttributeError, file_upload.save_tmpfile)
        self.assertFalse(os.path.exists(file_upload.tmp_path))

    def test_validate_file_no_data(self):
        self._create_tmp_file()
        event = ValidatorEvent(None, self._file)
        self.assertRaisesRegexp(ValidationError, '.*no metadata.*',
                                validate_file, event)

    def test_validate_file_already_exist(self):
        self._create_tmp_file()
        record = File(id=120,
                      external_id='CH-0001',
                      version=1,
                      user='testuser',
                      filepath='/tmp/120.txt',
                      file_metadata=json.dumps({'filesize': 6}))
        record.insert(flush=True)
        file_upload = self._file
        file = open(self._file.filepath, 'w')
        file.write('FOOBAR')
        file.close()
        event = ValidatorEvent(None, file_upload)
        self.assertRaisesRegexp(ValidationError, '.*file already exist.*',
                                validate_file, event)

    def test_validate_file_filesize_mismatch(self):
        self._create_tmp_file()
        record = File(id=120,
                      external_id='CH-0001',
                      version=1,
                      user='testuser',
                      file_metadata=json.dumps({'filesize': 4}))
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file)
        self.assertRaisesRegexp(ValidationError, '.*filesize does not match.*',
                                validate_file, event)

    def test_validate_file(self):
        self._create_tmp_file()
        record = File(id=120,
                      external_id='CH-0001',
                      version=1,
                      user='testuser',
                      file_metadata=json.dumps({'filesize': 6}))
        record.insert(flush=True)
        event = ValidatorEvent(None, self._file)
        self.assertIsNone(validate_file(event))
