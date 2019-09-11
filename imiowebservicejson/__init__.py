# -*- coding: utf-8 -*-

from imio.dataexchange.db import DBSession
from imio.dataexchange.db import DeclarativeBase
from imio.dataexchange.db import temporary_session
from imio.dataexchange.db.scripts.init_db import import_data
from imiowebservicejson.authentication import check_authentication
from imiowebservicejson.predicates import ImplementPredicate
from imiowebservicejson.predicates import VersionPredicate
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.settings import asbool
from sqlalchemy import engine_from_config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.bind = engine
    initialized_query = "select * from pg_tables where schemaname = 'public'"
    if engine.execute(initialized_query).rowcount < 4:
        DeclarativeBase.metadata.create_all()
        init_session = temporary_session(engine)
        import_data(init_session)
        init_session.close()

    settings["traceback.debug"] = asbool(settings.get("traceback.debug", "false"))
    authn_policy = BasicAuthAuthenticationPolicy(check_authentication)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        root_factory=Root,
    )
    # adds cornice
    config.include("cornice")
    config.include("cornice_swagger")

    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_route("home", "/")
    config.add_route("test", "/test/{webservice}/{commune}/{version}/{type}")
    config.add_route("schema", "/schema/{name}/{version}")
    config.add_route("dms_metadata", "/dms_metadata/{id}/{version}")
    config.add_route("dms_file_upload", "/file_upload/{version}/{id}")
    config.add_route("file_upload", "/file_upload/{id}")
    config.add_route("file_latest", "/file/{client_id}/{external_id}")
    config.add_route("file", "/file/{client_id}/{external_id}/{version}")

    config.add_subscriber_predicate("implement", ImplementPredicate)
    config.add_subscriber_predicate("version", VersionPredicate)
    config.scan(ignore=[".tests", ".models.tests", ".views.tests"])
    return config.make_wsgi_app()


class Root(object):
    __acl__ = [
        (Allow, Authenticated, "view"),
        (Allow, Authenticated, "query"),
        (Allow, Authenticated, "access"),
    ]

    def __init__(self, request):
        self.request = request
