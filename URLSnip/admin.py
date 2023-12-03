from collections.abc import Sequence
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.http.request import HttpRequest
from .models import *
# Register your models here.


class ShortURLAdmin(admin.ModelAdmin):
    list_display = ['alias', 'url_domain', 'user', 'modified', 'created']
    list_search = ['alias', 'url', 'user', 'modified', 'created']


admin.site.register(ShortURL, ShortURLAdmin)


class CustomUserAdmin(UserAdmin):
    ordering = ['-date_joined']
    list_display =  ('username','email','date_joined','is_superuser')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
