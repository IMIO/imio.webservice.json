# -*- coding: utf-8 -*-
from sqlalchemy import desc

from imio.dataexchange.db.mappers.file import File


class FileRender(object):

    def __init__(self, request):
        self.dms_file = File.first(
            client_id=request.matchdict.get('client_id'),
            external_id=request.matchdict.get('external_id'),
            order_by=[desc(File.id)],
        )

    def render(self):
        f = open(self.filepath, 'r')
        return f.read()

    @property
    def filepath(self):
        return self.dms_file.filepath
