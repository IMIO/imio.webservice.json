# -*- coding: utf-8 -*-

from imiowebservicejson.tests import TestAppBaseTestCase
from imio.dataexchange.db import temporary_session
from imio.dataexchange.db import DBSession
from imio.dataexchange.db.mappers.router import Router

import json


class TestRouterService(TestAppBaseTestCase):
    def test_post_basic(self):
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "url": "http://localhost",
        }
        result = self.app.post("/router", params=params)
        self.assertEqual("200 OK", result.status)
        self.assertEqual({"msg": "Route added"}, json.loads(result.body))

    def test_post_already_exist(self):
        route = Router(client_id="CLI", application_id="APP", url="http://localhost")
        session = temporary_session(DBSession.bind)
        session.add(route)
        session.commit()
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "url": "http://localhost",
        }
        result = self.app.post("/router", params=params)
        self.assertEqual("200 OK", result.status)
        self.assertEqual({"msg": "Route already exist"}, json.loads(result.body))

    def test_patch(self):
        route = Router(client_id="CLI", application_id="APP", url="http://localhost")
        session = temporary_session(DBSession.bind)
        session.add(route)
        session.commit()
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "url": "http://localhost2",
        }
        result = self.app.patch("/router", params=params)
        self.assertEqual("200 OK", result.status)
        self.assertEqual({"msg": "Route updated"}, json.loads(result.body))
        route = Router.first()
        self.assertEqual("http://localhost2", route.url)
        self.assertIsNotNone(route.update_date)

    def test_patch_not_exist(self):
        params = {
            "client_id": "CLI",
            "application_id": "APP",
            "url": "http://localhost2",
        }
        result = self.app.patch("/router", params=params)
        self.assertEqual("200 OK", result.status)
        self.assertEqual({"msg": "The route does not exist"}, json.loads(result.body))

    def test_get(self):
        route = Router(client_id="CLI", application_id="APP", url="http://localhost")
        session = temporary_session(DBSession.bind)
        session.add(route)
        session.commit()
        result = self.app.get("/route/CLI/APP")
        self.assertEqual("200 OK", result.status)
        self.assertEqual(
            {"client_id": "CLI", "application_id": "APP", "url": "http://localhost"},
            json.loads(result.body),
        )

    def test_get_not_exist(self):
        result = self.app.get("/route/CLI/APP")
        self.assertEqual("200 OK", result.status)
        self.assertEqual({"msg": "The route does not exist"}, json.loads(result.body))

    def test_delete(self):
        route = Router(client_id="CLI", application_id="APP", url="http://localhost")
        session = temporary_session(DBSession.bind)
        session.add(route)
        session.commit()
        result = self.app.delete("/route/CLI/APP")
        self.assertEqual("200 OK", result.status)
        self.assertEqual({"msg": "Route deleted"}, json.loads(result.body))
        self.assertEqual(0, Router.count())

    def test_delete_not_exist(self):
        result = self.app.delete("/route/CLI/APP")
        self.assertEqual("200 OK", result.status)
        self.assertEqual({"msg": "The route does not exist"}, json.loads(result.body))
