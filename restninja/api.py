import datetime
import random
import re

from django.http import HttpRequest
from django.urls import reverse, reverse_lazy
from ninja import NinjaAPI, Schema, Path
from htmx.api import router as htmx_router
from company.api import router as company_router

api = NinjaAPI(csrf=True)

api.add_router('/htmx/', htmx_router)
api.add_router('/company/', company_router)


@api.get('/hello', url_name='hello')
def hello(request):
    return 'Hello world'


@api.get('/item/{int:item_id}')
def read_item(request, item_id: int):
    return {'item_id': item_id}


@api.get('/events/{int:year}/{int:month}/{int:day}')
def events(request, year: int, month: int, day: int):
    return {'date': [year, month, day]}


class PathDate(Schema):
    year: int
    month: int
    day: int

    def value(self):
        return datetime.date(self.year, self.month, self.day)


@api.get('/events2/{int:year}/{int:month}/{int:day}')
def events2(request, date: PathDate = Path(...)):
    return {'date': date.value()}


weapons = ['Ninjato', 'Shuriken', 'Katana', 'Kama', 'Kunai', 'Naginata', 'Yari']


@api.get('/weapons')
def list_weapons(request, limit: int = 10, offset: int = 0):
    return weapons[offset: offset + limit]


@api.get('/weapons/search')
def search_weapons(request, q: str, offset: int = 0):
    results = [w for w in weapons if q.lower() in w.lower()]
    print(q, results)
    return results[offset: offset + 10]


from datetime import date


@api.get('/example')
def example(request, s: str = None, b: bool = None, d: date = None, i: int = None):
    return [s, b, d, i]


# Schema

import datetime
from typing import List, Optional, Any
from pydantic import Field
from ninja import Query, Schema


class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(None, alias='categories')


@api.get('/filter')
def events3(request, filters: Filters = Query(...)):
    return {'filters': filters.dict()}


# Request Body

class Item(Schema):
    name: str
    description: str = None
    price: float
    quantity: int


@api.post('/items')
def create(request, item: Item):
    return item


@api.put('/items/{int:item_id}')
def update(request, item_id: int, item: Item):
    return {'item_id': item_id, 'item': item.dict()}


@api.post('/items/{int:item_id}')
def update2(request, item_id: int, item: Item, q: str):
    return {'item_id': item_id, 'item': item.dict(), 'q': q}


# Form Data

from ninja import Form


@api.post('/login')
def login(request, username: str = Form(...), password: str = Form(...)):
    return {'username': username, 'password': '*****'}


@api.post('items2')
def create2(request, item: Item = Form(...)):
    return item


@api.post('items2/{int:item_id}')
def update3(request, item_id: int, q: str, item: Item=Form(...)):
    return {'item_id': item_id, 'item': item.dict(), 'q': q}


# Mapping Empty Form Field to Default

from pydantic.fields import ModelField
from typing import Generic, TypeVar

PydanticField = TypeVar('PydanticField')


class EmptyStrToDefault(Generic[PydanticField]):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: PydanticField, field: ModelField) -> PydanticField:
        if value == '':
            return field.default
        return value


class Item2(Schema):
    name: str
    description: str = None
    price: EmptyStrToDefault[float] = 0.0
    quantity: EmptyStrToDefault[int] = 0
    in_stock: EmptyStrToDefault[bool] = True


@api.post('items-blank-default')
def update4(request, item: Item2 = Form(...)):
    return item.dict()


# File upload

from ninja import File
from ninja.files import UploadedFile


@api.post('/upload')
def upload(request, file: UploadedFile = File(...)):
    data = file.read()
    return {'name': file.name, 'len': len(data)}


@api.post('/upload-many')
def upload_many(request, files: List[UploadedFile] = File(...)):
    return [f.name for f in files]


# Response Schema

from django.contrib.auth.models import User


class UserIn(Schema):
    username: str
    password: str


class UserOut(Schema):
    id: int
    username: str


@api.post('/users/', response=UserOut)
def create_user(request, data: UserIn):
    user = User(username=data.username)
    user.set_password(data.password)
    user.save()
    return user


# Nested object


class UserSchema(Schema):
    id: int
    first_name: str
    last_name: str


class TaskSchema(Schema):
    id: int
    title: str
    is_completed: bool
    owner: UserSchema = None


from task.models import Task


@api.get('/tasks', response=List[TaskSchema])
def tasks(request):
    queryset = Task.objects.select_related('owner')
    return list(queryset)


# Aliases


class TaskSchema2(Schema):
    id: int
    title: str
    completed: bool = Field(..., alias='is_completed')
    owner_first_name: str = Field(None, alias='owner.first_name')


@api.get('/tasks2', response=List[TaskSchema2])
def tasks2(request):
    queryset = Task.objects.select_related('owner')
    return list(queryset)


# Resolver


class TaskSchema3(Schema):
    id: int
    title: str
    is_completed: bool
    owner: Optional[str]
    lower_title: str

    @staticmethod
    def resolve_owner(obj):
        if not obj.owner:
            return
        return f"{obj.owner.first_name} {obj.owner.last_name}"

    def resolve_lower_title(self, obj):
        return self.title.lower()


@api.get('/tasks3', response=List[TaskSchema3])
def tasks3(request):
    queryset = Task.objects.select_related('owner')
    return list(queryset)


# Returning querysets


@api.get('/tasks4', response=List[TaskSchema3])
def task4(request):
    return Task.objects.all()


# Empty responses


@api.post('/no_content', response={204: None})
def no_content(request):
    return 204, None


# Model Schema


from django.contrib.auth.models import User
from ninja import ModelSchema


class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username', 'email', 'first_name', 'last_name']


@api.get('/users', response=List[UserSchema])
def list_users(request):
    qs = User.objects.all()
    return qs


# Overriding fields

from django.contrib.auth.models import Group


class GroupSchema(ModelSchema):
    class Config:
        model = Group
        model_fields = ['id', 'name']


class UserSchema(ModelSchema):
    groups: List[GroupSchema] = []

    class Config:
        model = User
        model_fields = ['id', 'username', 'email', 'first_name', 'last_name']


@api.get('/users2', response=List[UserSchema])
def list_users2(request):
    qs = User.objects.all()
    return qs


# create_schema

from ninja.orm import create_schema

UserSchema = create_schema(
    User,
    depth=1,
    fields=['id', 'username', 'groups']
)


@api.get('/users3', response=List[UserSchema])
def list_users3(request):
    qs = User.objects.all()
    return qs


# Overriding Pydantic Config
# Convert field name FirstName to -> first_name

def to_snake(string: str) -> str:
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', string).lower()


class SnakeModelSchema(Schema):
    FirstName: str
    LastName: str

    class Config(Schema.Config):
        alias_generator = to_snake


@api.get('/users4', response=List[SnakeModelSchema])
def list_users4(request):
    qs = User.objects.all()
    return qs


# Auth

from ninja.security import django_auth, HttpBearer


@api.get('/pets', auth=django_auth)
def pets(request):
    return f"Authenticated user {request.auth}"


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        if token == 'supersecret':
            return token


@api.get('/bearer', auth=AuthBearer())
def bearer(request):
    return {'token': request.auth}


def ip_whitelist(request):
    if request.META['REMOTE_ADDR'] == '127.0.0.1':
        return '127.0.0.1'


@api.get('/apiwhitelist', auth=ip_whitelist)
def ip_whitelist(request):
    return f"Authenticated client, IP = {request.auth}"


from ninja.security import APIKeyHeader


class ApiKey(APIKeyHeader):
    param_name = 'X-API-Key'

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        if key == 'supersecret':
            return key


header_key = ApiKey()


@api.get('/headerkey', auth=header_key)
def headerkey(request):
    return f"Token = {request.auth}"


from ninja.security import APIKeyCookie


class CookieKey(APIKeyCookie):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        if key == 'supersecret':
            return key

cookie_key = CookieKey()


@api.get('cookiekey', auth=cookie_key)
def cookiekey(request):
    return f"Token = {request.auth}"


from ninja.security import HttpBasicAuth


class BasicAuth(HttpBasicAuth):
    def authenticate(
        self, request: HttpRequest, username: str, password: str
    ) -> Optional[Any]:
        if username == 'admin' and password == 'secret':
            return username


@api.get('/basicauth', auth=BasicAuth())
def basicauth(request):
    return {'httpuser': request.auth}


# Multiple authenticators

from ninja.security import APIKeyQuery


class AuthCheck:
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        if key == 'supersecret':
            return key


class QueryKey(AuthCheck, APIKeyQuery):
    pass


class HeaderKey(AuthCheck, APIKeyHeader):
    pass


@api.get('/multipleauth', auth=[QueryKey(), HeaderKey()])
def multipleauth(request):
    return f"Token = {request.auth}"


# Custom exceptions

class InvalidToken(Exception):
    pass


@api.exception_handler(InvalidToken)
def on_invalid_token(request, e):
    return api.create_response(request, {'detail': 'Invalid token supplied'}, status=401)


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        if token == 'supersecret':
            return token
        raise InvalidToken


@api.get('bearer-custom-exception', auth=AuthBearer())
def bearer_custom_exception(request):
    return {'token': request.auth}


# Nested routers

from ninja import Router

first_router = Router(tags=['nested'])
second_router = Router(tags=['nested'])
third_router = Router(tags=['nested'])


@first_router.get('/add')
def add(request, a: int, b:int):
    return {'result': a + b}


@second_router.get('/add')
def add(request, a: int, b:int):
    return {'result': a + b}


@third_router.get('/add')
def add(request, a: int, b:int):
    return {'result': a + b}


second_router.add_router('l3', third_router)
first_router.add_router('l2', second_router)
api.add_router('l1', first_router)


# Reverse URLS


@api.get('/reverse', tags=['reverse'], operation_id='reverse', summary='Reverse URL')
def reverse(request):
    """
    Pastikan untuk meperhitungkan path parameter.

    **Ex: /users/{user_id}**

    Dan jadikan argument pada reverse_lazy
    """
    return {'hello': reverse_lazy('api-1.0.0:hello')}


@api.post("/make-order/", deprecated=True)
def some_old_method(request, order: str):
    return {"success": True}


# Custom exception handlers

class ServiceUnavailableError(Exception):
    pass


@api.exception_handler(ServiceUnavailableError)
def service_unavailable(request, e):
    return api.create_response(
        request,
        {'message': 'Please retry later'},
        status=503,
    )


@api.get('/service')
def some_operation(request):
    if random.choice([True, False]):
        raise ServiceUnavailableError()
    return {'message': 'Hello'}