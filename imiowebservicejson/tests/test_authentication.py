# -*- coding: utf-8 -*-

from imiowebservicejson.authentication import check_authentication

import hashlib
import unittest


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        settings = {
            "auth.login": "user",
            "auth.password": hashlib.md5(b"saltpwdsalt").hexdigest(),
            "auth.secret": "salt",
        }
        registry = type("registry", (object,), {"settings": settings})
        self.request = type("request", (object,), {"registry": registry})

    def test_valid_credentials(self):
        self.assertEqual([], check_authentication("user", "pwd", self.request))

    def test_wrong_password(self):
        self.assertIsNone(check_authentication("user", "wrong", self.request))

    def test_unknown_user(self):
        self.assertIsNone(check_authentication("other", "pwd", self.request))
