# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from pyramid.settings import asbool

from .predicates import ImplementPredicate
from .predicates import VersionPredicate


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['traceback.debug'] = asbool(settings.get('traceback.debug',
                                                      'false'))
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('test', '/test/{webservice}/{commune}/{version}/{type}')
    config.add_route('schema', '/schema/{name}/{version}')
    config.add_route('dms_metadata', '/dms_metadata/{client_id}/{version}')
    config.add_route('file', '/file/{id}')

    config.add_subscriber_predicate('implement', ImplementPredicate)
    config.add_subscriber_predicate('version', VersionPredicate)
    config.scan()
    return config.make_wsgi_app()
