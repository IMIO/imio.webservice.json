# -*- coding: utf-8 -*-

from datetime import datetime
from imio.dataexchange.db.mappers.file import File
from pyramid import security
from pyramid.view import view_config
from sqlalchemy import desc
import logging

from imiowebservicejson.fileupload import FileUpload
from imiowebservicejson.models.dms_metadata import DMSMetadata
from imiowebservicejson.views.base import exception_handler
from imiowebservicejson.views.base import failure
from imiowebservicejson.views.base import http_logging
from imiowebservicejson.views.base import json_logging
from imiowebservicejson.views.base import json_validator
from imiowebservicejson.views.base import validate_object


log = logging.getLogger(__name__)


@view_config(route_name='dms_metadata', renderer='json', permission='query')
@exception_handler()
@json_validator(schema_name='dms_metadata', model=DMSMetadata)
@json_logging(log)
def dms_metadata(request, input, response):
    userid = security.unauthenticated_userid(request)
    dms_file = File.first(user=userid,
                          external_id=input.external_id,
                          order_by=[desc(File.version)])
    if dms_file is None or input.update_flag is True and \
       dms_file.filepath is not None:
        version = File.count(user=userid, external_id=input.external_id) + 1
        dms_file = File()
        dms_file.version = version
        if input.update_flag is True:
            dms_file.update_date = datetime.now()
    else:
        dms_file.update_date = datetime.now()
    dms_file.external_id = input.external_id
    dms_file.client_id = input.client_id
    dms_file.type = input.document_type
    dms_file.user = userid
    dms_file.file_metadata = input.json_object
    dms_file.insert(flush=True)
    response.message = "Well done"
    response.id = dms_file.id
    response.external_id = input.external_id
    return response


@view_config(route_name='file_upload', renderer='json', permission='query')
@exception_handler()
@http_logging(log)
def file_upload(request):
    request.matchdict['version'] = '1.0'
    return dms_file_upload(request)


@view_config(route_name='dms_file_upload', renderer='json', permission='query')
@exception_handler()
@http_logging(log)
def dms_file_upload(request):
    upload = FileUpload(request)
    upload.save_tmpfile()

    error = validate_object(request, upload)
    if error is not None:
        return failure(str(error), error_code=getattr(error, 'code', None))

    upload.move()
    upload.save_reference()

    return {
        "success": True,
        "message": "File uploaded successfully"}
