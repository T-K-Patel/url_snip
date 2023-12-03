from django.urls import path
from . import views

urlpatterns = [
    path("", views.Home, name="home"),
    path("app", views.App, name="app"),
    path("login", views.Login, name="login"),
    path("forgotpassword", views.ForgotPassword, name="forgotpassword"),
    path("verify", views.VerifyEmail, name="otp_verification"),
    path("resetpassword", views.ResetPasssword, name="resetpassword"),
    path("logout", views.Logout, name="logout"),
    path("register", views.Register, name="register"),
    path("me", views.Profile, name="me"),
    path("activate/<str:token>", views.Activate, name="activate"),
    path("clean_users/", views.clean_users, name="clean_users"),
    path("<str:url>", views.GetShort, name="geturl"),
]
