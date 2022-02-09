import json
from typing import List, Any

import yaml
from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.types import DictStrAny


class MyYamlParser(Parser):
    def parse_body(self, request: HttpRequest) -> DictStrAny:
        return yaml.safe_load(request.body)


class PlainRenderer(BaseRenderer):
    media_type = 'text/plain'

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        return json.dumps(data)


api = NinjaAPI(version='2.0.0', parser=MyYamlParser(), renderer=PlainRenderer())


@api.get('/hello')
def hello(request):
    return {'message': 'Hello from v2'}


class Payload(Schema):
    ints: List[int]
    string: str
    f: float


@api.post('/yaml')
def post_yaml(request, payload: Payload):
    """
    Menerima request dengan format Yaml
    """
    return payload.dict()