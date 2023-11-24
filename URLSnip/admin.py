from django.contrib import admin
from .models import *
# Register your models here.
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ['alias', 'name', 'url', 'modified', 'created']
    list_search= ['alias', 'name', 'url', 'modified', 'created']
    

admin.site.register(ShortURL,ShortURLAdmin)