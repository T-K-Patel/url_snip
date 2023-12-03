from django.urls import path
from . import views

urlpatterns = [
    path("", views.Home, name="home"),
    path("app/", views.App, name="app"),
    path("<str:url>", views.GetShort, name="geturl"),
    path("login/", views.Login, name="login"),
    path("forgotpassword/", views.ForgotPassword, name="forgotpassword"),
    path("verify/", views.VerifyEmail, name="otp_verification"),
    path("resetpassword/", views.ResetPasssword, name="resetpassword"),
    path("logout/", views.Logout, name="logout"),
    path("register/", views.Logout, name="register"),
    path("me/", views.Profile, name="me"),
]