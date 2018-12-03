# -*- coding: utf-8 -*-

from cornice import Service
from cornice.validators import colander_body_validator
from imio.dataexchange.core import Request as RequestMessage
from imio.dataexchange.db.mappers.request import Request as RequestTable
from imiowebservicejson.request import SinglePublisher

import colander
import json
import uuid


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
    )


class GetRequestBodySchema(colander.MappingSchema):

    client_id = colander.SchemaNode(
        colander.String(),
        description='The id of the client',
    )

    request_id = colander.SchemaNode(
        colander.String(),
        description='The uid of the request',
    )


request = Service(
    name='request',
    path='/request',
    description='Get and post request for application',
)


@request.post(validators=(colander_body_validator, ),
              schema=PostRequestBodySchema())
def post_request(request):
    external_uid = uuid.uuid4().hex

    # Insert into the request queue
    amqp_url = request.registry.settings.get('rabbitmq.url')
    publisher = SinglePublisher('{0}/%2Fwebservice?connection_attempts=3&'
                                'heartbeat_interval=3600'.format(amqp_url))
    publisher.setup_queue('ws.request', 'request')
    internal_uid = '{0}-{1}'.format(
        request.validated['client_id'],
        external_uid,
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

    return {'uid': external_uid}


@request.get(validators=(colander_body_validator, ),
             schema=GetRequestBodySchema())
def get_request(request):
    internal_uid = '{0}-{1}'.format(
        request.validated['client_id'],
        request.validated['request_id'],
    )
    record = RequestTable.first(uid=internal_uid)
    if not record:
        return {'error': 'unknown request'}
    return {
        'request_id': request.validated['request_id'],
        'client_id': request.validated['client_id'],
        'response': json.loads(record.response),
    }
