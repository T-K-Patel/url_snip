from django.contrib import admin
from .models import *
# Register your models here.


class ShortURLAdmin(admin.ModelAdmin):
    list_display = ['alias', 'url', 'user', 'modified', 'created']
    list_search = ['alias', 'url', 'user', 'modified', 'created']


admin.site.register(ShortURL, ShortURLAdmin)
