# -*- coding: utf-8 -*-

import operator
import unittest
from distutils.version import StrictVersion

from zope.interface import Interface
from zope.interface import alsoProvides

from imiowebservicejson import predicates


class TestPredicates(unittest.TestCase):

    def test_implement_predicate(self):
        class TestInterface(Interface):
            pass

        predicate = predicates.ImplementPredicate(TestInterface, None)
        context = type('context', (object, ), {})()
        event = type('event', (object, ), {'context': context})()
        self.assertEqual(False, predicate(event))

        alsoProvides(event.context, TestInterface)
        self.assertEqual(True, predicate(event))

    def test_version_predicate(self):
        predicate = predicates.VersionPredicate(('>= 1.1', '<= 1.2'), None)
        matchdict = {'version': '1.0'}
        request = type('request', (object, ), {'matchdict': matchdict})()
        event = type('event', (object, ), {'request': request})()
        self.assertEqual(False, predicate(event))

        version_comparison = (('1.1', True), ('1.1.5', True), ('1.2', True),
                              ('1.2.1', False), ('1.3', False))

        for version, result in version_comparison:
            event.request.matchdict['version'] = version
            self.assertEqual(result, predicate(event))

    def test_get_operator_and_version(self):
        comparison = ((operator.gt, '1.0a1', '> 1.0a1'),
                      (operator.ge, '2.0.1', '>=2.0.1'),
                      (operator.eq, '0.1', '0.1'))
        for op, version, expr in comparison:
            self.assertEqual((op, StrictVersion(version)),
                             predicates.get_operator_and_version(expr))
