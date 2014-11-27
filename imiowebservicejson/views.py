# -*- coding: utf-8 -*-

from datetime import datetime
from jsonschema import validate, ValidationError
from sqlalchemy import desc
from warlock import model_factory
import cPickle
import traceback
import uuid

from pyramid import security
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import forget
from pyramid.view import view_config

from imio.dataexchange.db.mappers.file import File
from imio.dataexchange.db.mappers.request import Request

from imiowebservicejson.event import ValidatorEvent
from imiowebservicejson.filerender import FileRender
from imiowebservicejson.fileupload import FileUpload
from imiowebservicejson.schema import get_schemas
from imiowebservicejson.models.dms_metadata import DMSMetadata
from imiowebservicejson.models.test_request import TestRequest
from imiowebservicejson.models.test_response import TestResponse
from imiowebservicejson.request import SinglePublisher
from imiowebservicejson.request import Request as RequestMessage
from imiowebservicejson.request import RequestFile
from imiowebservicejson.request import SingleConsumer


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
        if input.update_flag is True:
            dms_file.update_date = datetime.now()
    else:
        dms_file.update_date = datetime.now()
    dms_file.external_id = input.external_id
    dms_file.client_id = input.client_id
    dms_file.type = input.type
    dms_file.user = userid
    dms_file.file_metadata = input.json_object
    dms_file.insert(flush=True)
    response.message = "Well done"
    response.id = dms_file.id
    response.external_id = input.external_id
    return response


@view_config(route_name='file_upload', renderer='json', permission='query')
@exception_handler()
def file_upload(request):
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


@view_config(route_name='file', renderer='string', permission='access')
def file(request):
    renderer = FileRender(request)
    if renderer.dms_file is None:
        raise HTTPNotFound
    return renderer.render()


@view_config(route_name='test_request', renderer='json', permission='query')
@exception_handler()
@json_validator(schema_name='test_request', model=TestRequest)
def test_request(request, input, response):
    uid = uuid.uuid4().hex

    amqp_url = request.registry.settings.get('rabbitmq.url')
    publisher = SinglePublisher('{0}/%2Frequest?connection_attempts=3&'
                                'heartbeat_interval=3600'.format(amqp_url))
    publisher.setup_queue('request.{0}.{1}'.format(input.application_id,
                                                   input.client_id),
                          input.client_id)
    msg = RequestMessage(input.request_type, input.request_parameters,
                         input.client_id, uid)
    record = Request(uid=uid)
    record.insert()
    if input.files:
        response.files_id = []
    for file in input.files:
        f_uid = uuid.uuid4().hex
        request_file = RequestFile(f_uid, file)
        msg.add_file(request_file)
        Request(uid=f_uid).insert()
        response.files_id.append(f_uid)

    publisher.add_message(msg)
    publisher.start()

    response.message = "Well done"
    response.request_id = uid
    return response


@view_config(route_name='test_response', renderer='json', permission='query')
@exception_handler()
@json_validator(schema_name='test_response', model=TestResponse)
def test_response(request, input, response):
    amqp_url = request.registry.settings.get('rabbitmq.url')
    consumer = SingleConsumer('{0}/%2Frequest?connection_attempts=3&'
                              'heartbeat_interval=3600'.format(amqp_url))
    consumer.queue = input.request_id
    consumer.routing_key = input.request_id
    consumer.start()
    message = consumer.get_message()
    if not message:
        response.success = False
        response.message = "No message"
    else:
        response.success = True
        response.message = "Well done"
        response.response = cPickle.loads(message)
        consumer.acknowledge_message()
    consumer.stop()
    return response


@view_config(context=HTTPForbidden)
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response
