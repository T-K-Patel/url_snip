from django.urls import path
from . import views

urlpatterns = [
    path("", views.Home, name="home"),
    path("app/", views.App, name="app"),
    path("<str:url>", views.GetShort, name="geturl"),
    path("temp/", views.LoadTemp, name="temp"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    path("register/", views.Logout, name="register"),
    path("me/", views.Profile, name="me"),
]