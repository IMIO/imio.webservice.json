# -*- coding: utf-8 -*-

from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('json', '/json/{webservice}/{commune}/{version}/{type}')
    config.add_route('schema', '/schema/{name}/{version}')
    config.add_route('file', '/file/{id}')
    config.add_subscriber_predicate('implement', ImplementPredicate)
    config.add_subscriber_predicate('version', VersionPredicate)
    config.scan('.models.test_schema')
    config.scan()
    return config.make_wsgi_app()


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
