# -*- coding: utf-8 -*-

from imio.dataexchange.db import DBSession
from imio.dataexchange.db import temporary_session
from imiowebservicejson import main
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from webtest import TestApp

import unittest
import os


class TestAppBaseTestCase(unittest.TestCase):

    def setUp(self):
        cwd = os.path.dirname(__file__)
        settings = appconfig('config:%s' % os.path.join(cwd, '../test.ini'))
        self.app = TestApp(main({}, **settings))

    def tearDown(self):
        session = temporary_session(DBSession.bind)
        delete_tables = ('router', 'request')
        for table in delete_tables:
            session.execute('delete from {0}'.format(table))
        session.commit()
        testing.tearDown()
