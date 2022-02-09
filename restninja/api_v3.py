from typing import Any

import orjson
from django.http import HttpRequest
from ninja import NinjaAPI
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.types import DictStrAny


class ORJSONParser(Parser):
    def parse_body(self, request: HttpRequest) -> DictStrAny:
        return orjson.loads(request.body)


class ORJSONRenderer(BaseRenderer):
    media_type = 'application/json'

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        return orjson.dumps(data)


api = NinjaAPI(version='3.0.0', parser=ORJSONParser(), renderer=ORJSONRenderer())


@api.get('/hello')
def hello(request):
    return {'message': 'Hello from v3'}