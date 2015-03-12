# -*- coding: utf-8 -*-

from pyramid.view import view_config
import logging

from imiowebservicejson.schema import get_schemas
from imiowebservicejson.views.base import http_logging
from imiowebservicejson.views.base import exception_handler
from imiowebservicejson.views.base import failure


log = logging.getLogger(__name__)


@view_config(route_name='schema', renderer='json', permission='view')
@exception_handler()
@http_logging(log)
def schema(request):
    schema_name = request.matchdict.get('name')
    version = request.matchdict.get('version')
    input_schema, output_schema = get_schemas(schema_name, version)

    if input_schema is None or output_schema is None:
        msg = u"The asked schema '%s %s' doesn't exist" % (schema_name, version)
        return failure(msg, error_code='UNKNOWN_SCHEMA')

    definition = {'%s_in' % schema_name: input_schema,
                  '%s_out' % schema_name: output_schema}

    return {
        'success': True,
        'schemas': definition}
