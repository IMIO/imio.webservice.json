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


router = Service(
    name='router',
    path='/router',
    description='Register and get application for clients'
)


@router.post(validators=(colander_body_validator, ),
             schema=PostRouterSubscriptionSchema())
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


@router.patch(validators=(colander_body_validator, ),
              schema=PostRouterSubscriptionSchema())
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


@router.delete(validators=(colander_body_validator, ),
               schema=PostRouterSubscriptionSchema())
def delete_router(request):
    parameters = {
        'client_id': request.validated['client_id'],
        'application_id': request.validated['application_id'],
    }
    existing_route = RouterTable.first(**parameters)
    if not existing_route:
        return {'msg': 'The route does not exist'}
    existing_route.delete()
    return {'msg': 'Route deleted'}


@router.get(validators=(colander_body_validator, ),
            schema=PostRouterSubscriptionSchema())
def get_router(request):
    parameters = {
        'client_id': request.validated['client_id'],
        'application_id': request.validated['application_id'],
    }
    existing_route = RouterTable.first(**parameters)
    if not existing_route:
        return {'msg': 'The route does not exist'}
    return {
        'client_id': parameters['client_id'],
        'application_id': parameters['application_id'],
        'url': existing_route.url,
    }
