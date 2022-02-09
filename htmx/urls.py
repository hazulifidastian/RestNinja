from django.contrib import admin
from django.urls import path
from .views import hello, contact


urlpatterns = [
    path("hello", hello),
    path("contact/", contact)
]
