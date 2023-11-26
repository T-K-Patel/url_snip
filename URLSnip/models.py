from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ShortURL(models.Model):
    alias = models.CharField(max_length=25,unique=True)
    url = models.URLField()
    user=models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)
    modified = models.DateTimeField(auto_now=True,editable=False)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.alias
    