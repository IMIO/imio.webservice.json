# -*- coding: utf-8 -*-

from imiowebservicejson.scripts import cleanup
from imio.dataexchange.db import temporary_session
from imio.dataexchange.db.mappers.file import File
from imio.dataexchange.db.mappers.file_type import FileType
from imio.dataexchange.db import DBSession
from datetime import datetime

import unittest
import mock


class TestCleanup(unittest.TestCase):
    def _cleanup_database(self):
        self.session.execute("delete from file")
        self.session.execute("delete from file_type")
        self.session.commit()

    def setUp(self):
        self.session = temporary_session(DBSession.bind.engine)
        self._cleanup_database()
        self.session.add(FileType(
            id="COUR_E",
            description="Courrier Entrant",
        ))
        self.session.flush()
        self.session.add(File(
            external_id="E001",
            client_id="C001",
            type="COUR_E",
            version=1,
            date=datetime(2019, 1, 1),
            update_date=None,
            user="test",
            file_metadata={"external_id": "E001", "client_id": "C001"},
            filepath="/tmp/E001",
        ))
        self.session.add(File(
            external_id="E002",
            client_id="C001",
            type="COUR_E",
            version=1,
            date=datetime(2019, 1, 1),
            update_date=datetime(2019, 2, 1),
            user="test",
            file_metadata={"external_id": "E002", "client_id": "C001"},
            filepath="/tmp/E002",
        ))
        self.session.add(File(
            external_id="E003",
            client_id="C001",
            type="COUR_E",
            version=1,
            date=datetime(2019, 1, 1),
            update_date=None,
            user="test",
            file_metadata={"external_id": "E003", "client_id": "C001"},
            filepath=None,
        ))
        self.session.add(File(
            external_id="E004",
            client_id="C001",
            type="COUR_E",
            version=1,
            date=datetime(2019, 2, 1),
            update_date=None,
            user="test",
            file_metadata={"external_id": "E003", "client_id": "C001"},
            filepath="/tmp/E004",
        ))
        self.session.commit()

    def tearDown(self):
        self._cleanup_database()

    @mock.patch("os.path.exists", mock.Mock(side_effect=[True, False]))
    @mock.patch("os.remove")
    def test_remove_file(self, mock_remove):
        cls = cleanup.FileCleaner({})
        cls.remove_file("/tmp/foo/bar")
        self.assertTrue(mock_remove.called)
        self.assertEqual(1, mock_remove.call_count)
        cls.remove_file("/tmp/foo/blu")
        self.assertEqual(1, mock_remove.call_count)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 2, 2)),
    )
    @mock.patch("os.path.exists", mock.Mock(return_value=True))
    @mock.patch("os.remove")
    def test_clean(self, mock_remove):
        cls = cleanup.FileCleaner({})
        cls.get_session = mock.Mock(return_value=self.session)
        record = self.session.query(File).filter(File.external_id == "E001").first()
        self.assertIsNotNone(record.filepath)
        cls.clean(30)
        self.assertTrue(mock_remove.called)
        self.assertEqual(1, mock_remove.call_count)
        record = self.session.query(File).filter(File.external_id == "E001").first()
        self.assertIsNone(record.filepath)
