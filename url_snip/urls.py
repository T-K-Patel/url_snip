from django.contrib import admin
from django.urls import path, include


admin.site.site_title = 'URL Snip'
admin.site.site_header = 'URL Snip'
admin.site.index_title = 'Admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('URLSnip.urls')),
]
