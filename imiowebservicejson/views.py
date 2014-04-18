# -*- coding: utf-8 -*-
import json
import traceback
from datetime import datetime
from jsonschema import validate, ValidationError
from sqlalchemy import desc
from warlock import model_factory

from pyramid import security
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import forget
from pyramid.view import view_config

from .event import ValidatorEvent
from .fileupload import FileUpload
from .schema import get_schemas
from .mappers.file import File
from .models.dms_metadata import DMSMetadata


def exception_handler(message=u"An error occured during the process"):
    def decorator(func):
        def replacement(request):
            try:
                return func(request)
            except Exception as e:
                if request.registry.settings.get('traceback.debug') is True:
                    print traceback.format_exc()
                return failure(message, error=str(e))
        return replacement
    return decorator


def json_validator(schema_name, model):
    def decorator(func):
        def replacement(request):
            version = request.matchdict.get('version')
            input_schema, output_schema = get_schemas(schema_name, version)
            if input_schema is None or output_schema is None:
                msg = u"The schema '%s %s' doesn't exist" % (schema_name, version)
                return failure(msg)

            input_json = request.json_body
            error = validate_json_schema(input_json, input_schema)
            if error is not None:
                return failure(error)

            input_model = model_factory(input_schema, base_class=model)
            input = input_model(**input_json)
            error = validate_object(request, input)
            if error is not None:
                return failure(error)

            output_model = model_factory(output_schema)
            response = output_model(success=True, message="")
            return func(request, input, response)
        return replacement
    return decorator


def failure(message, error=None):
    msg = {"success": False, "message": message}
    if error is not None:
        msg['error'] = error
    return msg


def validate_json_schema(input_json, schema):
    try:
        validate(input_json, schema)
    except ValidationError, ve_obj:
        msg = 'Validation error'
        if len(ve_obj.path):
            msg += " on '%s'" % ', '.join(ve_obj.path)
        return u"%s: %s" % (msg, ve_obj.message)


def validate_object(request, obj):
    notify = request.registry.notify
    try:
        notify(ValidatorEvent(request, obj))
    except ValidationError as e:
        return str(e)


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {'project': 'imio.webservice.json'}


@view_config(route_name='schema', renderer='json', permission='view')
@exception_handler()
def schema(request):
    schema_name = request.matchdict.get('name')
    version = request.matchdict.get('version')
    input_schema, output_schema = get_schemas(schema_name, version)

    if input_schema is None or output_schema is None:
        msg = u"The asked schema '%s %s' doesn't exist" % (schema_name, version)
        return failure(msg)

    definition = {'%s_in' % schema_name: input_schema,
                  '%s_out' % schema_name: output_schema}

    return {
        'success': True,
        'schemas': definition}


@view_config(route_name='dms_metadata', renderer='json', permission='query')
@exception_handler()
@json_validator(schema_name='dms_metadata', model=DMSMetadata)
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
    else:
        dms_file.update_date = datetime.now()
    dms_file.external_id = input.external_id
    dms_file.user = userid
    dms_file.file_metadata = json.dumps(request.json)
    dms_file.insert(flush=True)
    response.message = "Well done"
    response.id = dms_file.id
    response.external_id = input.external_id
    return response


@view_config(route_name='file', renderer='json', permission='query')
@exception_handler()
def file(request):
    upload = FileUpload(request)
    upload.save_tmpfile()

    error = validate_object(request, upload)
    if error is not None:
        return failure(error)

    upload.move()
    upload.save_reference()

    return {
        "success": True,
        "message": "File uploaded successfully"}


@view_config(context=HTTPForbidden)
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response
