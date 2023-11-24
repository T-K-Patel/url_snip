from django.db import models

# Create your models here.
class ShortURL(models.Model):
    alias = models.CharField(max_length=25,unique=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    url = models.URLField()
    modified = models.DateTimeField(auto_now=True,editable=False)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name or self.alias
    