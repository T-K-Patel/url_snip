from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def validate_url(value):
    validator = URLValidator()
    try:
        validator(value)
    except:
        raise ValidationError(f"Invalid URL.")

# Create your models here.


class ShortURL(models.Model):
    alias = models.CharField(max_length=25, unique=True)
    url = models.TextField(max_length=1000, validators=[validate_url])
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alias
