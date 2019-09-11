# -*- coding: utf-8 -*-

from datetime import datetime
from imio.dataexchange.core import Request as RequestMessage
from imio.dataexchange.db import temporary_session
from imio.dataexchange.db import DBSession
from imio.dataexchange.db.mappers.request import Request
from imio.dataexchange.db.mappers.router import Router
from imiowebservicejson.scripts.requesthandler import BaseRequestHandler

import unittest
import mock
import json


class MockedPublisher(object):
    def __init__(self, url):
        self.url = url
        self.initialized = False
        self.published = False
        self.messages = []

    def setup_queue(self, queue_name, key):
        self.initialized = True
        self.queue_name = queue_name
        self.key = key

    def add_message(self, message):
        self.messages.append(message)

    def start(self):
        self.published = True


class MockedRequest(object):
    def __init__(self, result):
        self._result = result

    def json(self):
        return json.loads(self._result)


class TestRequestHandler(unittest.TestCase):
    def _cleanup_database(self):
        self.session.execute("delete from request")
        self.session.execute("delete from router")
        self.session.commit()

    def setUp(self):
        self.session = temporary_session(DBSession.bind.engine)
        self._cleanup_database()
        self.handler = BaseRequestHandler("")
        self.handler.get_session = mock.Mock(return_value=self.session)
        self.handler.error_count = 10
        self.session.add(Request(uid="CLI-APP-ABC", internal_uid="CLI-APP-XYZ"))
        self.session.add(
            Router(client_id="CLI", application_id="APP", url="http://localhost")
        )
        self.session.add(
            Router(client_id="CLI", application_id="APP2", url="http://localhost/")
        )
        self.session.commit()

    def tearDown(self):
        self._cleanup_database()

    def _get_message(
        self,
        type="GET",
        path="/path",
        app="APP",
        uid="CLI-APP-ABC",
        cache_duration=None,
        ignore_cache=False,
    ):
        return RequestMessage(
            type,
            path,
            {"foo": "bar"},
            app,
            "CLI",
            uid,
            cache_duration=cache_duration,
            ignore_cache=ignore_cache,
        )

    def test_get_url(self):
        message = self._get_message()
        url = self.handler.get_url(message, self.session)
        self.assertEqual("http://localhost/path", url)

    def test_get_url_url_with_extra_slash(self):
        message = self._get_message(app="APP2", path="bar")
        url = self.handler.get_url(message, self.session)
        self.assertEqual("http://localhost/bar", url)

    def test_get_url_url_with_path_without_slash(self):
        message = self._get_message(path="foo")
        url = self.handler.get_url(message, self.session)
        self.assertEqual("http://localhost/foo", url)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    @mock.patch("requests.patch")
    @mock.patch("requests.put")
    def test_make_request_get(self, r_put, r_patch, r_post, r_get):
        message = self._get_message(type="GET")
        self.handler.make_request(message, "http://localhost/path")
        self.assertTrue(r_get.called)
        self.assertFalse(r_post.called)
        self.assertFalse(r_patch.called)
        self.assertFalse(r_put.called)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    @mock.patch("requests.patch")
    @mock.patch("requests.put")
    def test_make_request_post(self, r_put, r_patch, r_post, r_get):
        message = self._get_message(type="POST")
        self.handler.make_request(message, "http://localhost/path")
        self.assertFalse(r_get.called)
        self.assertTrue(r_post.called)
        self.assertFalse(r_patch.called)
        self.assertFalse(r_put.called)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    @mock.patch("requests.patch")
    @mock.patch("requests.put")
    def test_make_request_patch(self, r_put, r_patch, r_post, r_get):
        message = self._get_message(type="PATCH")
        self.handler.make_request(message, "http://localhost/path")
        self.assertFalse(r_get.called)
        self.assertFalse(r_post.called)
        self.assertTrue(r_patch.called)
        self.assertFalse(r_put.called)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    @mock.patch("requests.patch")
    @mock.patch("requests.put")
    def test_make_request_put(self, r_put, r_patch, r_post, r_get):
        message = self._get_message(type="PUT")
        self.handler.make_request(message, "http://localhost/path")
        self.assertFalse(r_get.called)
        self.assertFalse(r_post.called)
        self.assertFalse(r_patch.called)
        self.assertTrue(r_put.called)

    def test_get_cache_no_cache(self):
        """Test when there is no cache"""
        cache = self.handler.get_cache(self.session, "CLI-APP-XYZ")
        self.assertEqual((None, None), cache)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    def test_get_cache_with_cache(self):
        """Test when there is a cached response"""
        expiration = datetime(2019, 6, 1, 10, 20)
        self.session.add(
            Request(
                uid="CLI-APP-XXX",
                internal_uid="CLI-APP-XYZ",
                response="{}",
                expiration_date=expiration,
            )
        )
        self.session.flush()

        cache = self.handler.get_cache(self.session, "CLI-APP-XYZ")
        self.assertEqual(("{}", expiration), cache)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    def test_get_cache_expired_cache(self):
        """Test with an expired cache"""
        self.session.add(
            Request(
                uid="CLI-APP-XXX",
                internal_uid="CLI-APP-XYZ",
                response="{}",
                expiration_date=datetime(2019, 6, 1, 10, 5),
            )
        )
        self.session.flush()

        cache = self.handler.get_cache(self.session, "CLI-APP-XYZ")
        self.assertEqual((None, None), cache)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    def test_get_cache_no_expiration_date_cache(self):
        """Test when the expiration date is undefined"""
        self.session.add(
            Request(uid="CLI-APP-XXX", internal_uid="CLI-APP-XYZ", response="{}")
        )
        self.session.flush()

        cache = self.handler.get_cache(self.session, "CLI-APP-XYZ")
        self.assertEqual((None, None), cache)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    def test_get_cache_when_ignored(self):
        """Test a special usecase when a recent response from an ignored cache request
        have an expiration date lesser than one another cached response"""
        expiration = datetime(2019, 6, 1, 10, 20)
        self.session.add(
            Request(
                uid="CLI-APP-XXX",
                internal_uid="CLI-APP-XYZ",
                response="{}",
                expiration_date=datetime(2019, 6, 1, 10, 30),
            )
        )
        self.session.commit()
        self.session.add(
            Request(
                uid="CLI-APP-YYY",
                internal_uid="CLI-APP-XYZ",
                response="{}",
                expiration_date=expiration,
            )
        )
        self.session.commit()

        cache = self.handler.get_cache(self.session, "CLI-APP-XYZ")
        self.assertEqual(("{}", expiration), cache)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    def test_get_cache_when_error(self):
        """Test when there was a result but it was an error"""
        self.session.add(
            Request(
                uid="CLI-APP-XXX",
                internal_uid="CLI-APP-XYZ",
                response='{"error": "An error occured"}',
                expiration_date=None,
            )
        )
        self.session.flush()

        cache = self.handler.get_cache(self.session, "CLI-APP-XYZ")
        self.assertEqual((None, None), cache)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.make_request",
        mock.Mock(return_value=MockedRequest("{}")),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.get_cache",
        mock.Mock(return_value=(None, None)),
    )
    def test_treat_message_basic(self):
        with mock.patch("imiowebservicejson.request.SinglePublisher") as publisher:
            publisher.return_value = MockedPublisher("url")
            message = self._get_message()
            self.handler.treat_message(message)
            self.assertFalse(publisher.return_value.initialized)
            record = Request.first(internal_uid="CLI-APP-XYZ", session=self.session)
            self.assertEqual("{}", record.response)
            self.assertEqual(datetime(2019, 6, 1, 10, 15), record.expiration_date)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.make_request",
        mock.Mock(return_value=MockedRequest("{}")),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.get_cache",
        mock.Mock(return_value=('{"foo":"bar"}', datetime(2019, 6, 1, 11, 10))),
    )
    def test_treat_message_ignored_cache(self):
        with mock.patch("imiowebservicejson.request.SinglePublisher") as publisher:
            publisher.return_value = MockedPublisher("url")
            message = self._get_message(ignore_cache=True)
            self.handler.treat_message(message)
            self.assertFalse(publisher.return_value.initialized)
            record = Request.first(internal_uid="CLI-APP-XYZ", session=self.session)
            self.assertEqual("{}", record.response)
            self.assertEqual(datetime(2019, 6, 1, 10, 15), record.expiration_date)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.make_request",
        mock.Mock(return_value=MockedRequest("{}")),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.get_cache",
        mock.Mock(return_value=('{"foo":"bar"}', datetime(2019, 6, 1, 11, 10))),
    )
    def test_treat_message_cached(self):
        with mock.patch("imiowebservicejson.request.SinglePublisher") as publisher:
            publisher.return_value = MockedPublisher("url")
            message = self._get_message()
            self.handler.treat_message(message)
            self.assertFalse(publisher.return_value.initialized)
            record = Request.first(internal_uid="CLI-APP-XYZ", session=self.session)
            self.assertEqual('{"foo":"bar"}', record.response)
            self.assertEqual(datetime(2019, 6, 1, 11, 10), record.expiration_date)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.make_request",
        mock.Mock(side_effect=ValueError),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.get_cache",
        mock.Mock(return_value=(None, None)),
    )
    def test_treat_message_error(self):
        with mock.patch("imiowebservicejson.request.SinglePublisher") as publisher:
            publisher.return_value = MockedPublisher("url")
            message = self._get_message()
            self.handler.treat_message(message)
            self.assertTrue(publisher.return_value.initialized)
            self.assertTrue(publisher.return_value.published)
            record = Request.first(internal_uid="CLI-APP-XYZ", session=self.session)
            self.assertIsNone(record.response)
            self.assertIsNone(record.expiration_date)
            self.assertEqual(1, message.error_count)

    @mock.patch(
        "imiowebservicejson.utils.now",
        mock.Mock(return_value=datetime(2019, 6, 1, 10, 10)),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.make_request",
        mock.Mock(side_effect=ValueError("An error occured")),
    )
    @mock.patch(
        "imiowebservicejson.scripts.requesthandler.BaseRequestHandler.get_cache",
        mock.Mock(return_value=(None, None)),
    )
    def test_treat_message_too_much_errors(self):
        with mock.patch("imiowebservicejson.request.SinglePublisher") as publisher:
            publisher.return_value = MockedPublisher("url")
            message = self._get_message()
            message.error_count = 10
            self.handler.treat_message(message)
            self.assertFalse(publisher.return_value.initialized)
            self.assertFalse(publisher.return_value.published)
            record = Request.first(internal_uid="CLI-APP-XYZ", session=self.session)
            self.assertEqual('{"error": "An error occured"}', record.response)
            self.assertIsNone(record.expiration_date)
