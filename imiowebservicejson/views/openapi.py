# -*- coding: utf-8 -*-

from cornice import Service
from cornice.service import get_services
from cornice_swagger import CorniceSwagger


swagger = Service(name="OpenAPI", path="/__api__", description="OpenAPI documentation")


@swagger.get()
def open_api_spec(request):
    doc = CorniceSwagger(get_services())
    my_spec = doc.generate("IMIO Internal REST API", "1.0.0")
    return my_spec
