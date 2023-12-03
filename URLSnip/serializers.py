from datetime import datetime
import humanize
from rest_framework import serializers
from . models import *
import random
import string
reserved_paths = ['admin', 'temp', 'login', 'logout', 'activate',
                  'register', 'verify', 'resetpassword', 'forgotpassword', 'me']


def generateShort(length=7):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def getDelay(timet):
    dt_object = datetime.utcfromtimestamp(int(datetime.timestamp(timet)))
    time_ago = humanize.naturaltime(datetime.utcnow() - dt_object)
    return time_ago


class ShortURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortURL
        fields = ['alias', 'url', 'user']

    def validate(self, attrs):
        if attrs.get('alias') and len(attrs.get('alias')) < 5:
            raise serializers.ValidationError({"alias": "Invalid length"})
        if attrs.get('alias') in reserved_paths:
            raise serializers.ValidationError({"alias": "reserved"})
        return super().validate(attrs)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.created:
            data['created'] = getDelay(instance.created)
        return data
