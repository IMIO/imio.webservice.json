# -*- coding: utf-8 -*-
from sqlalchemy import desc

from imio.dataexchange.db.mappers.file import File


class FileRender(object):

    def __init__(self, request):
        filters = {
            'client_id': request.matchdict.get('client_id'),
            'external_id': request.matchdict.get('external_id'),
            'order_by': [desc(File.id)],
        }
        if request.matchdict.get('version'):
            filters['version'] = request.matchdict.get('version')
        self.dms_file = self.get_file(**filters)

    def get_file(self, **kwargs):
        return File.first(**kwargs)

    def render(self):
        f = open(self.filepath, 'r')
        return f.read()

    @property
    def filepath(self):
        return self.dms_file.filepath
