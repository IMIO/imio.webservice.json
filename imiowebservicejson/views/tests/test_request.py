# -*- coding: utf-8 -*-

from datetime import datetime
from imio.dataexchange.db import DBSession
from imio.dataexchange.db import temporary_session
from imio.dataexchange.db.mappers.request import Request as RequestTable
from imiowebservicejson.tests import TestAppBaseTestCase
from imiowebservicejson.views import request

import json
import mock


class FakeMD5(object):
    def __init__(self, hexdigest):
        self._hexdigest = hexdigest

    def hexdigest(self):
        return self._hexdigest


class TestRequestService(TestAppBaseTestCase):
    """Tests requests views"""

    @mock.patch(
        "uuid.uuid4", mock.Mock(return_value=type("obj", (object,), {"hex": "ABC"})())
    )
    def test_generate_external_uid_basic_post(self):
        body = {
            "path": "/test",
            "request_type": "POST",
            "application_id": "APP",
            "client_id": "CLI",
            "parameters": {"foo": "bar"},
        }
        external_uid = request.generate_external_uid(body)
        self.assertEqual("ABC", external_uid)

    def test_generate_external_uid_basic_get(self):
        body = {
            "path": "/test",
            "request_type": "GET",
            "application_id": "APP",
            "client_id": "CLI",
            "parameters": {"foo": "bar"},
        }
        external_uid = request.generate_external_uid(body)
        self.assertEqual("2d4a3cfef68790d69eb102c5937311fc", external_uid)

    def test_generate_external_uid_get_with_cache(self):
        body = {
            "client_id": "CLI",
            "application_id": "APP",
            "path": "/test",
            "request_type": "GET",
            "ignore_cache": True,
            "cache_duration": 1000,
            "parameters": {"foo": "bar"},
        }
        external_uid = request.generate_external_uid(body)
        self.assertEqual("2d4a3cfef68790d69eb102c5937311fc", external_uid)

    @mock.patch("hashlib.md5", mock.Mock(return_value=FakeMD5("ABC")))
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_request_get(self, mocked_start, mocked_add_message):
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "GET",
            "path": "/test",
            "parameters": {},
        }
        result = self.app.post("/request", params=params)
        self.assertTrue(mocked_add_message.called)
        self.assertTrue(mocked_start.called)
        self.assertEqual("200 OK", result.status)
        self.assertEqual(
            {u"request_id": u"ABC", u"client_id": u"CLI", u"application_id": u"APP"},
            json.loads(result.body),
        )

    @mock.patch("hashlib.md5", mock.Mock(return_value=FakeMD5("ABC")))
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_duplicate_request_get(self, mocked_start, mocked_add_message):
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "GET",
            "path": "/test",
            "parameters": {},
        }
        results = [
            self.app.post("/request", params=params),
            self.app.post("/request", params=params),
        ]
        self.assertEqual(1, mocked_add_message.call_count)
        self.assertEqual(1, mocked_start.call_count)
        self.assertListEqual(["200 OK", "200 OK"], [e.status for e in results])
        for element in results:
            self.assertEqual(
                {
                    u"request_id": u"ABC",
                    u"client_id": u"CLI",
                    u"application_id": u"APP",
                },
                json.loads(element.body),
            )

    @mock.patch("hashlib.md5", mock.Mock(return_value=FakeMD5("ABC")))
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_duplicate_ignored_cache_request_get(
        self, mocked_start, mocked_add_message
    ):
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "GET",
            "path": "/test",
            "parameters": {},
            "ignore_cache": True,
        }
        results = [
            self.app.post("/request", params=params),
            self.app.post("/request", params=params),
        ]
        self.assertEqual(1, mocked_add_message.call_count)
        self.assertEqual(1, mocked_start.call_count)
        self.assertListEqual(["200 OK", "200 OK"], [e.status for e in results])
        for element in results:
            self.assertEqual(
                {
                    u"request_id": u"ABC",
                    u"client_id": u"CLI",
                    u"application_id": u"APP",
                },
                json.loads(element.body),
            )

    @mock.patch("hashlib.md5", mock.Mock(return_value=FakeMD5("ABC")))
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_without_expiration(self, mocked_start, mocked_add_message):
        """ Test the post_request when there is a result but without expiration date """
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "GET",
            "path": "/test",
            "parameters": {},
        }
        request_record = RequestTable(uid="CLI-APP-ABC")
        session = temporary_session(DBSession.bind)
        session.add(request_record)
        session.commit()
        result = self.app.post("/request", params=params)
        self.assertFalse(mocked_add_message.called)
        self.assertFalse(mocked_start.called)
        self.assertEqual("200 OK", result.status)
        self.assertEqual(
            {u"request_id": u"ABC", u"client_id": u"CLI", u"application_id": u"APP"},
            json.loads(result.body),
        )

    @mock.patch("hashlib.md5", mock.Mock(return_value=FakeMD5("ABC")))
    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 1, 1, 12, 0, 0)),
    )
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_not_expired(self, mocked_start, mocked_add_message):
        """ Test the post_request when there is a result and the expiration date
        is in the future """
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "GET",
            "path": "/test",
            "parameters": {},
        }
        request_record = RequestTable(
            uid="CLI-APP-ABC",
            expiration_date=datetime(2019, 1, 1, 12, 5, 0, 0),
            response="response",
        )
        session = temporary_session(DBSession.bind)
        session.add(request_record)
        session.commit()
        result = self.app.post("/request", params=params)
        self.assertFalse(mocked_add_message.called)
        self.assertFalse(mocked_start.called)
        self.assertEqual("200 OK", result.status)
        self.assertEqual(
            {u"request_id": u"ABC", u"client_id": u"CLI", u"application_id": u"APP"},
            json.loads(result.body),
        )
        record = RequestTable.first(uid="CLI-APP-ABC")
        self.assertEqual(datetime(2019, 1, 1, 12, 5, 0, 0), record.expiration_date)
        self.assertEqual("response", record.response)

    @mock.patch("hashlib.md5", mock.Mock(return_value=FakeMD5("ABC")))
    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 1, 1, 12, 0, 0)),
    )
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_ignore_cache(self, mocked_start, mocked_add_message):
        """ Test the post_request when there is a result, the expiration date
        is in the future and the ignore_cache parameter is used"""
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "GET",
            "path": "/test",
            "ignore_cache": True,
            "parameters": {},
        }
        request_record = RequestTable(
            uid="CLI-APP-ABC",
            expiration_date=datetime(2019, 1, 1, 12, 5, 0, 0),
            response="response",
        )
        session = temporary_session(DBSession.bind)
        session.add(request_record)
        session.commit()
        result = self.app.post("/request", params=params)
        self.assertTrue(mocked_add_message.called)
        self.assertTrue(mocked_start.called)
        self.assertEqual("200 OK", result.status)
        self.assertEqual(
            {u"request_id": u"ABC", u"client_id": u"CLI", u"application_id": u"APP"},
            json.loads(result.body),
        )
        record = RequestTable.first(uid="CLI-APP-ABC")
        self.assertIsNone(record.expiration_date)
        self.assertIsNone(record.response)

    @mock.patch("hashlib.md5", mock.Mock(return_value=FakeMD5("ABC")))
    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 1, 1, 12, 0, 0)),
    )
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_expired(self, mocked_start, mocked_add_message):
        """ Test the post_request when there is a result and the expiration date
        is in the past """
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "GET",
            "path": "/test",
            "parameters": {},
        }
        request_record = RequestTable(
            uid="CLI-APP-ABC",
            expiration_date=datetime(2019, 1, 1, 11, 55, 0, 0),
            response="response",
        )
        session = temporary_session(DBSession.bind)
        session.add(request_record)
        session.commit()
        result = self.app.post("/request", params=params)
        self.assertTrue(mocked_add_message.called)
        self.assertTrue(mocked_start.called)
        self.assertEqual("200 OK", result.status)
        self.assertEqual(
            {u"request_id": u"ABC", u"client_id": u"CLI", u"application_id": u"APP"},
            json.loads(result.body),
        )
        record = RequestTable.first(uid="CLI-APP-ABC")
        self.assertIsNone(record.expiration_date)
        self.assertIsNone(record.response)

    @mock.patch(
        "uuid.uuid4", mock.Mock(return_value=type("o", (object,), {"hex": "ABC"})())
    )
    @mock.patch("imiowebservicejson.request.SinglePublisher.start")
    @mock.patch("imiowebservicejson.request.SinglePublisher.add_message")
    def test_post_request_post(self, mocked_start, mocked_add_message):
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "request_type": "POST",
            "path": "/test",
            "parameters": {},
        }
        result = self.app.post("/request", params=params)
        self.assertTrue(mocked_add_message.called)
        self.assertTrue(mocked_start.called)
        self.assertEqual("200 OK", result.status)
        self.assertEqual(
            {u"request_id": u"ABC", u"client_id": u"CLI", u"application_id": u"APP"},
            json.loads(result.body),
        )
