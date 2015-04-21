# -*- coding: utf-8 -*-

import operator
import re
from distutils.version import StrictVersion


class ImplementPredicate(object):

    def __init__(self, interface, config):
        self.interface = interface

    def text(self):
        return "event object implement %s" % self.interface

    phash = text

    def __call__(self, event):
        return self.interface.providedBy(event.context)


class VersionPredicate(object):

    def __init__(self, versions, config):
        if isinstance(versions, basestring):
            versions = (versions, )
        self.versions = versions

    def text(self):
        return "versions %s" % ", ".join(self.versions)

    phash = text

    def __call__(self, event):
        current_version = StrictVersion(event.request.context.version)
        for expression in self.versions:
            op, version = get_operator_and_version(expression)
            if op(current_version, version) is False:
                return False
        return True


def get_operator_and_version(expression):
    """ Return the operator and the version from an expression e.g >= 2.0.1 """

    op_string = re.search('[>=<!]{0,2}', expression).group()
    version = expression.replace(op_string, '').strip()
    return get_operator(op_string), StrictVersion(version)


def get_operator(string):
    """ Return the associated python operator function """
    op_dict = {'>': operator.gt,
               '<': operator.lt,
               '>=': operator.ge,
               '=>': operator.ge,
               '<=': operator.le,
               '=<': operator.le,
               '==': operator.eq,
               '!=': operator.ne}
    return op_dict.get(string, operator.eq)
