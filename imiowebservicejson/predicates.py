# -*- coding: utf-8 -*-


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
        self.versions = versions

    def text(self):
        return "versions %s" % ", ".join(self.versions)

    phash = text

    def __call__(self, event):
        version = event.request.context.version
        for expression in self.versions:
            if eval(version + expression) is False:
                return False
        return True
