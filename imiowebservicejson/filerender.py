# -*- coding: utf-8 -*-
from imio.dataexchange.db.mappers.file import File
from pyramid.response import FileResponse
from sqlalchemy import desc


class FileRender(object):
    def __init__(self, request):
        self.request = request
        filters = {
            "client_id": request.matchdict.get("client_id"),
            "external_id": request.matchdict.get("external_id"),
            "order_by": [desc(File.id)],
        }
        if request.matchdict.get("version"):
            filters["version"] = request.matchdict.get("version")
        self.dms_file = self.get_file(**filters)

    def get_file(self, **kwargs):
        return File.first(**kwargs)

    def render(self):
        # Files are binary (pdf, odt...): stream the bytes, the view renderer is skipped
        return FileResponse(self.filepath, request=self.request)

    @property
    def filepath(self):
        return self.dms_file.filepath
