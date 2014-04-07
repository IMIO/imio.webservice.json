# -*- coding: utf-8 -*-
import os
import shutil
from jsonschema import validate, ValidationError
from warlock import model_factory

from pyramid.view import view_config

from .exception import ValidationError
from .schema import get_schemas
from .models.test_schema import TestSchema


def exception_handler(message=u"An error occured during the process"):
    def decorator(func):
        def replacement(request):
            try:
                return func(request)
            except Exception as e:
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

            json = request.json_body
            error = validate_json_schema(json, input_schema)
            if error is not None:
                return failure(error)

            input_model = model_factory(input_schema, base_class=model)
            input = input_model(**json)
            error = validate_model(request, input)
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


def validate_json_schema(json, schema):
    try:
        validate(json, schema)
    except ValidationError, ve_obj:
        msg = 'Validation error'
        if len(ve_obj.path):
            msg += " on '%s'" % ', '.join(ve_obj.path)
        return u"%s: %s" % (msg, ve_obj.message)


def validate_model(request, obj):
    notify = request.registry.notify
    from .event import ValidatorEvent
    try:
        notify(ValidatorEvent(request, obj))
    except ValidationError as e:
        return str(e)


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'imio.webservice.json'}


@view_config(route_name='schema', renderer='json')
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


@view_config(route_name='json', renderer='json')
@exception_handler()
@json_validator(schema_name='test_schema', model=TestSchema)
def json_view(request, input, response):
    json_file = open(input.filepath, 'wb')
    json_file.write(request.body)
    json_file.close()
    response.message = "Well done"
    response.id = str(input.uid)
    return response


@view_config(route_name='file', renderer='json')
@exception_handler()
def file(request):
    request_file = request.POST['filedata']
    ext = os.path.splitext(request_file.filename)[-1]
    filename = '%(name)s%(ext)s' % {'name': request.matchdict.get('id'),
                                    'ext': ext}

    tmp_path = '/tmp/%s' % filename
    input_file = request_file.file
    output_file = open(tmp_path, 'wb')

    input_file.seek(0)
    while True:
        data = input_file.read(2<<16)
        if not data:
            break
        output_file.write(data)

    shutil.move(tmp_path, '/home/vagrant/file/%s' % filename)

    return {
        "success": True,
        "message": "File uploaded successfully"}
