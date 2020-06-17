# -*- coding: utf-8 -*-

from cornice import Service
from cornice.validators import colander_body_validator
from cornice.validators import colander_querystring_validator
from imio.dataexchange.core import Request as RequestMessage
from imio.dataexchange.db.mappers.request import Request as RequestTable
from imiowebservicejson import request as rq

import colander
import hashlib
import json
import uuid


def generate_internal_uid(client_id, application_id, external_uid):
    """Generate the internal uid (stored in the database)"""
    return "{0}-{1}-{2}".format(client_id, application_id, external_uid)


def generate_internal_hash(body):
    """Generate the internal hash uid based on the request body"""
    if body["request_type"] == "GET":
        filtered_body = {
            k: v for k, v in body.items() if k not in ("ignore_cache", "cache_duration")
        }
        return hashlib.md5(json.dumps(filtered_body)).hexdigest()
    return uuid.uuid4().hex


def generate_uid():
    """Generate the external uid"""
    return uuid.uuid4().hex


def generate_uids(body):
    internal_hash = generate_internal_hash(body)
    external_hash = generate_uid()
    external_uid = generate_internal_uid(
        body["client_id"],
        body["application_id"],
        external_hash,
    )
    internal_uid = generate_internal_uid(
        body["client_id"],
        body["application_id"],
        internal_hash,
    )
    return external_hash, external_uid, internal_uid


class PostRequestBodySchema(colander.MappingSchema):

    client_id = colander.SchemaNode(
        colander.String(), description="The id of the client"
    )

    application_id = colander.SchemaNode(
        colander.String(), description="The id of the application"
    )

    request_type = colander.SchemaNode(
        colander.String(), description="The type of the request"
    )

    path = colander.SchemaNode(
        colander.String(), description="The path to the application"
    )

    cache_duration = colander.SchemaNode(
        colander.Integer(), description="The cache duration in seconds", missing=300
    )

    ignore_cache = colander.SchemaNode(
        colander.Boolean(),
        description="Ignore existing cache (if present)",
        missing=False,
    )

    parameters = colander.SchemaNode(
        colander.Mapping(unknown="preserve"),
        description="The parameters of the request",
        missing=colander.drop,
    )


class GetRequestBodySchema(colander.MappingSchema):

    request_id = colander.SchemaNode(
        colander.String(), description="The uid of the request"
    )

    client_id = colander.SchemaNode(
        colander.String(), description="The id of the client"
    )

    application_id = colander.SchemaNode(
        colander.String(), description="The id of the application"
    )


class PostRequestResponseSchema(colander.MappingSchema):

    request_id = colander.SchemaNode(
        colander.String(), description="The uid of the request"
    )

    client_id = colander.SchemaNode(
        colander.String(), description="The id of the client"
    )

    application_id = colander.SchemaNode(
        colander.String(), description="The id of the application"
    )

    cache_duration = colander.SchemaNode(
        colander.Integer(), description="The cache duration in seconds", missing=300
    )

    ignore_cache = colander.SchemaNode(
        colander.Boolean(),
        description="Ignore existing cache (if present)",
        missing=False,
    )


class PostRequestSuccessResponseSchema(colander.MappingSchema):
    body = PostRequestResponseSchema()


post_response_schemas = {
    "200": PostRequestSuccessResponseSchema(description="Return value")
}


class GetRequestResponseSchema(colander.MappingSchema):

    request_id = colander.SchemaNode(
        colander.String(), description="The uid of the request"
    )

    client_id = colander.SchemaNode(
        colander.String(), description="The id of the client"
    )

    application_id = colander.SchemaNode(
        colander.String(), description="The id of the application"
    )

    response = colander.SchemaNode(
        colander.Mapping(unknown="preserve"), description="The response of the request"
    )


class GetRequestSuccessResponseSchema(colander.MappingSchema):
    body = GetRequestResponseSchema()


get_response_schemas = {
    "200": GetRequestSuccessResponseSchema(description="Return value"),
    "204": GetRequestSuccessResponseSchema(description="Return value"),
    "404": GetRequestSuccessResponseSchema(description="Return value"),
}


request = Service(
    name="request", path="/request", description="Get and post request for application"
)


@request.post(
    validators=(colander_body_validator,),
    schema=PostRequestBodySchema(),
    response_schemas=post_response_schemas,
)
def post_request(request):
    # Insert into the request queue
    amqp_url = request.registry.settings.get("rabbitmq.url")
    publisher_parameters = "connection_attempts=3&heartbeat_interval=3600"
    publisher = rq.SinglePublisher(
        "{0}/%2Fwebservice?{1}".format(amqp_url, publisher_parameters)
    )
    if request.validated.get("request_type") == "GET":
        queue_key = "read"
    else:
        queue_key = "write"
    publisher.setup_queue(
        "ws.request.{0}".format(queue_key), "request.{0}".format(queue_key)
    )
    external_hash, external_uid, internal_uid = generate_uids(request.validated)
    result = {
        "request_id": external_hash,
        "client_id": request.validated["client_id"],
        "application_id": request.validated["application_id"],
    }
    msg = RequestMessage(
        request.validated["request_type"],
        request.validated["path"],
        request.validated.get("parameters", {}),
        request.validated["application_id"],
        request.validated["client_id"],
        external_uid,
        cache_duration=request.validated["cache_duration"],
        ignore_cache=request.validated["ignore_cache"]
    )

    record = RequestTable(uid=external_uid, internal_uid=internal_uid)
    record.insert()
    publisher.add_message(msg)
    publisher.start()
    return result


def request_get_validator(request, **kwargs):
    if request.body:
        validator = colander_body_validator
        kwargs["schema"].name = "body"
    else:
        validator = colander_querystring_validator
        kwargs["schema"].name = "querystring"
    validator(request, **kwargs)


@request.get(
    validators=(request_get_validator,),
    schema=GetRequestBodySchema(),
    response_schemas=get_response_schemas,
)
def get_request(request):
    request_id = request.validated["request_id"]
    external_uid = generate_internal_uid(
        request.validated["client_id"], request.validated["application_id"], request_id
    )
    record = RequestTable.first(uid=external_uid)
    result = {
        "request_id": request_id,
        "client_id": request.validated["client_id"],
        "application_id": request.validated["application_id"],
        "response": "",
    }
    if not record:
        request.response.status_code = 404
        return result
    if not record.response:
        request.response.status_code = 204
        return result
    result["response"] = json.loads(record.response)
    return result
