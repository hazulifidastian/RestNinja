from io import StringIO
from typing import Any

from django.http import HttpRequest
from django.utils.encoding import force_str
from django.utils.xmlutils import SimplerXMLGenerator
from ninja import NinjaAPI
from ninja.renderers import BaseRenderer


class XMLRenderer(BaseRenderer):
    media_type = "text/xml"

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        stream = StringIO()
        xml = SimplerXMLGenerator(stream, 'utf-8')
        xml.startDocument()
        xml.startElement('data', {})
        self._to_xml(xml, data)
        xml.endElement('data')
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml: SimplerXMLGenerator, data: Any):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement('item', {})
                self._to_xml(xml, item)
                xml.endElement('item')

        elif isinstance(data, dict):
            for key, value in data.items():
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(force_str(data))


api = NinjaAPI(version='4.0.0', renderer=XMLRenderer())


@api.get('/hello')
def hello(request):
    return {'message': 'Hello from v3'}