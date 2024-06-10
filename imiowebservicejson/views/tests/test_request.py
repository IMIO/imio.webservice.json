# -*- coding: utf-8 -*-

from imiowebservicejson.tests import TestAppBaseTestCase
from imiowebservicejson.views import request

from . import json
import mock


class FakeMD5(object):
    def __init__(self, hexdigest):
        self._hexdigest = hexdigest

    def hexdigest(self):
        return self._hexdigest


class TestRequestService(TestAppBaseTestCase):
    """Tests requests views"""

    def test_generate_internal_uid(self):
        self.assertEqual("A-B-C", request.generate_internal_uid("A", "B", "C"))
        self.assertEqual("1-2-3", request.generate_internal_uid("1", "2", "3"))

    @mock.patch(
        "uuid.uuid4", mock.Mock(return_value=type("obj", (object,), {"hex": "ABC"})())
    )
    def test_generate_internal_hash_basic_post(self):
        body = {
            "path": "/test",
            "request_type": "POST",
            "application_id": "APP",
            "client_id": "CLI",
            "parameters": {"foo": "bar"},
        }
        external_uid = request.generate_internal_hash(body)
        self.assertEqual("ABC", external_uid)

    def test_generate_internal_hash_basic_get(self):
        body = {
            "path": "/test",
            "request_type": "GET",
            "application_id": "APP",
            "client_id": "CLI",
            "parameters": {"foo": "bar"},
        }
        external_uid = request.generate_internal_hash(body)
        self.assertEqual("2d4a3cfef68790d69eb102c5937311fc", external_uid)

    def test_generate_internal_hash_with_cache(self):
        body = {
            "client_id": "CLI",
            "application_id": "APP",
            "path": "/test",
            "request_type": "GET",
            "ignore_cache": True,
            "cache_duration": 1000,
            "parameters": {"foo": "bar"},
        }
        external_uid = request.generate_internal_hash(body)
        self.assertEqual("2d4a3cfef68790d69eb102c5937311fc", external_uid)

    @mock.patch(
        "imiowebservicejson.views.request.generate_internal_hash",
        mock.Mock(return_value="XYZ"),
    )
    @mock.patch(
        "imiowebservicejson.views.request.generate_uid", mock.Mock(return_value="ABC")
    )
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
