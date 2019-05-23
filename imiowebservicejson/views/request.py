# -*- coding: utf-8 -*-

from cornice import Service
from cornice.validators import colander_body_validator
from imio.dataexchange.core import Request as RequestMessage
from imio.dataexchange.db.mappers.request import Request as RequestTable
from imiowebservicejson import request as rq

import colander
import json
import uuid


def generate_uids(client_id, application_id, external_uid=None):
    """Generate internal and external uids"""
    if external_uid is None:
        external_uid = uuid.uuid4().hex
    internal_uid = '{0}-{1}-{2}'.format(
        client_id,
        application_id,
        external_uid,
    )
    return internal_uid, external_uid


class PostRequestBodySchema(colander.MappingSchema):

    client_id = colander.SchemaNode(
        colander.String(),
        description='The id of the client',
    )

    application_id = colander.SchemaNode(
        colander.String(),
        description='The id of the application',
    )

    request_type = colander.SchemaNode(
        colander.String(),
        description='The type of the request',
    )

    path = colander.SchemaNode(
        colander.String(),
        description='The path to the application',
    )

    parameters = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        description='The parameters of the request',
        missing=colander.drop,
    )


class GetRequestBodySchema(colander.MappingSchema):

    request_id = colander.SchemaNode(
        colander.String(),
        description='The uid of the request',
    )

    client_id = colander.SchemaNode(
        colander.String(),
        description='The id of the client',
    )

    application_id = colander.SchemaNode(
        colander.String(),
        description='The id of the application',
    )


class PostRequestResponseSchema(colander.MappingSchema):

    request_id = colander.SchemaNode(
        colander.String(),
        description='The uid of the request',
    )

    client_id = colander.SchemaNode(
        colander.String(),
        description='The id of the client',
    )

    application_id = colander.SchemaNode(
        colander.String(),
        description='The id of the application',
    )


class PostRequestSuccessResponseSchema(colander.MappingSchema):
    body = PostRequestResponseSchema()


post_response_schemas = {
    '200': PostRequestSuccessResponseSchema(description='Return value'),
}


class GetRequestResponseSchema(colander.MappingSchema):

    request_id = colander.SchemaNode(
        colander.String(),
        description='The uid of the request',
    )

    client_id = colander.SchemaNode(
        colander.String(),
        description='The id of the client',
    )

    application_id = colander.SchemaNode(
        colander.String(),
        description='The id of the application',
    )

    response = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        description='The response of the request',
    )


class GetRequestSuccessResponseSchema(colander.MappingSchema):
    body = GetRequestResponseSchema()


get_response_schemas = {
    '200': GetRequestSuccessResponseSchema(description='Return value'),
    '204': GetRequestSuccessResponseSchema(description='Return value'),
    '404': GetRequestSuccessResponseSchema(description='Return value'),
}


request = Service(
    name='request',
    path='/request',
    description='Get and post request for application',
)


@request.post(validators=(colander_body_validator, ),
              schema=PostRequestBodySchema(),
              response_schemas=post_response_schemas)
def post_request(request):

    # Insert into the request queue
    amqp_url = request.registry.settings.get('rabbitmq.url')
    publisher_parameters = 'connection_attempts=3&heartbeat_interval=3600'
    publisher = rq.SinglePublisher(
        '{0}/%2Fwebservice?{1}'.format(amqp_url, publisher_parameters),
    )
    publisher.setup_queue('ws.request', 'request')
    internal_uid, external_uid = generate_uids(
        client_id=request.validated['client_id'],
        application_id=request.validated['application_id'],
    )
    msg = RequestMessage(
        request.validated['request_type'],
        request.validated['path'],
        request.validated.get('parameters', {}),
        request.validated['application_id'],
        request.validated['client_id'],
        internal_uid,
    )

    record = RequestTable(uid=internal_uid)
    record.insert()
    publisher.add_message(msg)
    publisher.start()

    return {
        'request_id': external_uid,
        'client_id': request.validated['client_id'],
        'application_id': request.validated['application_id'],
    }


@request.get(validators=(colander_body_validator, ),
             schema=GetRequestBodySchema(),
             response_schemas=get_response_schemas)
def get_request(request):
    internal_uid, external_uid = generate_uids(
        client_id=request.validated['client_id'],
        application_id=request.validated['application_id'],
        external_uid=request.validated['request_id'],
    )
    record = RequestTable.first(uid=internal_uid)
    result = {
        'request_id': external_uid,
        'client_id': request.validated['client_id'],
        'application_id': request.validated['application_id'],
        'response': "",
    }
    if not record:
        request.response.status_code = 404
        return result
    if not record.response:
        request.response.status_code = 204
        return result
    result['response'] = json.loads(record.response)
    return result
