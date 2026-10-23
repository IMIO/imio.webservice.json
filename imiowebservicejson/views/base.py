# -*- coding: utf-8 -*-

from imiowebservicejson import utils
from imiowebservicejson.db import get_session
from imiowebservicejson.event import ValidatorEvent
from imiowebservicejson.schema import get_schemas
from jsonschema import validate, ValidationError
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import forget
from pyramid.view import view_config
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import StatementError
from warlock import model_factory

import traceback


def json_logging(logger):
    def decorator(func):
        def replacement(request, input, response):
            logger.info('REQUEST : %s - %s' % (request.url,
                                               input.json_object))
            return_value = func(request, input, response)
            logger.info('RESPONSE : %s - %s' % (request.url, return_value))
            return return_value
        return replacement
    return decorator


def http_logging(logger):
    def decorator(func):
        def replacement(request):
            logger.info('REQUEST : %s' % request.url)
            return_value = func(request)
            logger.info('RESPONSE : %s' % return_value)
            return return_value
        return replacement
    return decorator


def exception_handler(message=u"An error occured during the process"):
    def decorator(func):
        def replacement(request):
            try:
                return func(request)
            except Exception as e:
                if request.registry.settings.get('traceback.debug') is True:
                    print(traceback.format_exc())
                return failure(
                    message,
                    error=str(e),
                    error_code=getattr(e, 'code', None),
                )
        return replacement
    return decorator


def json_validator(schema_name, model):
    def decorator(func):
        def replacement(request):
            version = request.matchdict.get('version')
            input_schema, output_schema = get_schemas(schema_name, version)
            if input_schema is None or output_schema is None:
                msg = u"The schema '%s %s' doesn't exist" % (schema_name, version)
                return failure(msg, error_code='INTERNAL_ERROR')

            input_json = request.json_body
            error = validate_json_schema(input_json, input_schema)
            if error is not None:
                return failure(error, error_code='SCHEMA_VALIDATION_ERROR')

            input_model = model_factory(input_schema, base_class=model)
            input = input_model(**input_json)
            error = validate_object(request, input)
            if error is not None:
                return failure(str(error),
                               error_code=getattr(error, 'code', None))

            output_model = model_factory(output_schema)
            response = output_model(success=True, message="")
            return func(request, input, response)
        return replacement
    return decorator


def failure(message, error=None, error_code=None):
    result = {'success': False, 'message': message}
    result['error_code'] = error_code and error_code or 'INTERNAL_ERROR'
    if error is not None:
        result['error'] = error
    return result


def validate_json_schema(input_json, schema):
    try:
        validate(input_json, schema)
    except ValidationError as ve_obj:
        msg = 'Validation error'
        if len(ve_obj.path):
            msg += " on '%s'" % ', '.join(ve_obj.path)
        return u"%s: %s" % (msg, ve_obj.message)


def validate_object(request, obj):
    notify = request.registry.notify
    try:
        notify(ValidatorEvent(request, obj))
    except ValidationError as e:
        return e


def temporary_session(func):
    def replacement(request):
        session = get_session(request)
        try:
            utils.test_temporary_session(session)
        except (OperationalError, InvalidRequestError, StatementError):
            # Some errors may happen during rollback
            session.remove()
            session = get_session(request)
        try:
            result = func(request, session)
        except Exception as e:
            raise e
        return result
    return replacement


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {'project': 'imio.webservice.json'}


@view_config(context=HTTPForbidden)
def basic_challenge(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response
