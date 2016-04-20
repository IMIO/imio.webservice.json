# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from imiowebservicejson.filerender import FileRender


@view_config(route_name='file_latest', renderer='string', permission='access')
def file_latest(request):
    renderer = FileRender(request)
    if renderer.dms_file is None:
        raise HTTPNotFound
    return renderer.render()


@view_config(route_name='file', renderer='string', permission='access')
def file(request):
    renderer = FileRender(request)
    if renderer.dms_file is None:
        raise HTTPNotFound
    return renderer.render()
