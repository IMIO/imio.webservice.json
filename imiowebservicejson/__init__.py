# -*- coding: utf-8 -*-
from pyramid.config import Configurator

from .predicates import ImplementPredicate
from .predicates import VersionPredicate


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
