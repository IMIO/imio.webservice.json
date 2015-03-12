# -*- coding: utf-8 -*-

from pyramid.view import view_config
from imio.dataexchange.core import Request as RequestMessage
from imio.dataexchange.core import RequestFile
from imio.dataexchange.db.mappers.request import Request
import cPickle
import logging
import uuid

from imiowebservicejson.views.base import exception_handler
from imiowebservicejson.views.base import json_logging
from imiowebservicejson.views.base import json_validator
from imiowebservicejson.models.test_request import TestRequest
from imiowebservicejson.models.test_response import TestResponse
from imiowebservicejson.request import SinglePublisher
from imiowebservicejson.request import SingleConsumer


log = logging.getLogger(__name__)


@view_config(route_name='test_request', renderer='json', permission='query')
@exception_handler()
@json_validator(schema_name='test_request', model=TestRequest)
@json_logging(log)
def test_request(request, input, response):
    uid = uuid.uuid4().hex

    amqp_url = request.registry.settings.get('rabbitmq.url')
    publisher = SinglePublisher('{0}/%2Fwsrequest?connection_attempts=3&'
                                'heartbeat_interval=3600'.format(amqp_url))
    publisher.setup_queue('{0}.{1}.{2}'.format(input.application_id,
                                               input.request_type,
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
@json_logging(log)
def test_response(request, input, response):
    amqp_url = request.registry.settings.get('rabbitmq.url')
    consumer = SingleConsumer('{0}/%2Fwsresponse?connection_attempts=3&'
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
        response.response = cPickle.loads(message).parameters
        consumer.acknowledge_message()
    consumer.stop()
    return response
