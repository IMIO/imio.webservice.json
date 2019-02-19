# -*- coding: utf-8 -*-

from cornice import Service
from cornice.validators import colander_body_validator
from imio.dataexchange.db.mappers.router import Router as RouterTable
from datetime import datetime

import colander


class PostRouterSubscriptionSchema(colander.MappingSchema):

    client_id = colander.SchemaNode(
        colander.String(),
        description='The id of the client',
    )

    application_id = colander.SchemaNode(
        colander.String(),
        description='The id of the application',
    )

    url = colander.SchemaNode(
        colander.String(),
        description='The url of the application',
    )


class RouterResponseSchema(colander.MappingSchema):
    msg = colander.SchemaNode(
        colander.String(),
        description='The response message',
    )


class RoutesSchema(colander.SequenceSchema):
    route = PostRouterSubscriptionSchema()


class DiscoveryRouterSchema(colander.MappingSchema):
    routes = RoutesSchema()


class RouterSuccessResponseSchema(colander.MappingSchema):
    body = RouterResponseSchema()


class RouterGetSuccessResponseSchema(colander.MappingSchema):
    body = PostRouterSubscriptionSchema()


class RouterDiscoverySuccessResponseSchema(colander.MappingSchema):
    body = DiscoveryRouterSchema()


response_schemas = {
    '200': RouterSuccessResponseSchema(description='Return value'),
}

get_response_schemas = {
    '200': RouterGetSuccessResponseSchema(description='Return value'),
}

discovery_response_schemas = {
    '200': RouterDiscoverySuccessResponseSchema(description='Return value'),
}


router_post = Service(
    name='router',
    path='/router',
    description='Register and update application for clients',
)

router_get = Service(
    name='route',
    path='/route/{client_id}/{application_id}',
    description='Get and delete application for clients',
)

route_discovery = Service(
    name='route_discovery',
    path='/route/{client_id}',
    description='Discover routes for a client',
)


@router_post.post(validators=(colander_body_validator, ),
                  schema=PostRouterSubscriptionSchema(),
                  response_schemas=response_schemas)
def post_router(request):
    parameters = {
        'client_id': request.validated['client_id'],
        'application_id': request.validated['application_id'],
        'url': request.validated['url'],
    }
    existing_route = RouterTable.first(**parameters)
    if existing_route:
        return {'msg': 'Route already exist'}
    record = RouterTable(**parameters)
    record.insert()
    return {'msg': 'Route added'}


@router_post.patch(validators=(colander_body_validator, ),
                   schema=PostRouterSubscriptionSchema(),
                   response_schemas=response_schemas)
def patch_router(request):
    parameters = {
        'client_id': request.validated['client_id'],
        'application_id': request.validated['application_id'],
    }
    existing_route = RouterTable.first(**parameters)
    if not existing_route:
        return {'msg': 'The route does not exist'}
    existing_route.url = request.validated['url']
    existing_route.update_date = datetime.now()
    existing_route.update()
    return {'msg': 'Route updated'}


@router_get.delete(response_schemas=response_schemas)
def delete_router(request):
    parameters = {
        'client_id': request.matchdict['client_id'],
        'application_id': request.matchdict['application_id'],
    }
    existing_route = RouterTable.first(**parameters)
    if not existing_route:
        return {'msg': 'The route does not exist'}
    existing_route.delete()
    return {'msg': 'Route deleted'}


@router_get.get(response_schemas=get_response_schemas)
def get_router(request):
    parameters = {
        'client_id': request.matchdict['client_id'],
        'application_id': request.matchdict['application_id'],
    }
    existing_route = RouterTable.first(**parameters)
    if not existing_route:
        return {'msg': 'The route does not exist'}
    return {
        'client_id': parameters['client_id'],
        'application_id': parameters['application_id'],
        'url': existing_route.url,
    }


@route_discovery.get(response_schemas=discovery_response_schemas)
def get_discovery_route(request):
    parameters = {
        'client_id': request.matchdict['client_id'],
    }
    routes = RouterTable.get(**parameters)
    if not routes:
        return {'msg': 'There is no route for this client'}
    return {
        'routes': [{
            'client_id': parameters['client_id'],
            'application_id': r.application_id,
            'url': r.url,
        } for r in routes]
    }
