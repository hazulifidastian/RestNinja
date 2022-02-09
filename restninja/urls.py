from django.contrib import admin
from django.urls import path, include as url_include
from .api import api
from .api_v2 import api as api_v2
from .api_v3 import api as api_v3
from .api_v4 import api as api_v4

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
    path("htmx/", url_include(("htmx.urls"))),
    path('api/v2/', api_v2.urls),
    path('api/v3/', api_v3.urls),
    path('api/v4/', api_v4.urls),
]
