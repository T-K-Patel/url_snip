from django.urls import path
from . import views

urlpatterns = [
    path("", views.Home, name="home"),
    path("<str:url>", views.GetShort, name="GetURL")
]
