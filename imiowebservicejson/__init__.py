# -*- coding: utf-8 -*-
from sqlalchemy import engine_from_config

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.settings import asbool

from .authentication import check_authentication
from .db import DBSession
from .db import DeclarativeBase
from .predicates import ImplementPredicate
from .predicates import VersionPredicate


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.bind = engine

    settings['traceback.debug'] = asbool(settings.get('traceback.debug',
                                                      'false'))
    authn_policy = BasicAuthAuthenticationPolicy(check_authentication)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        root_factory=Root,
    )
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


class Root(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
        (Allow, Authenticated, 'query'),
    ]

    def __init__(self, request):
        self.request = request
