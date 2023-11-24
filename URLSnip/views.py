import datetime
import random
import string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.views import Response, APIView
from . models import ShortURL
from .serializers import *
from . import forms
# Create your views here.


def generateShort(length=7):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def GetShort(request, url):
    url = get_object_or_404(ShortURL, alias=url)
    url.save()
    return redirect(url.url)


def Home(request):
    # ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    if request.method == "POST":
        data = {"alias": request.POST.get('alias'), "url": request.POST.get(
            'url'), "name": request.POST.get('name')}
        auto = False
        if not request.POST.get('alias'):
            data['alias'] = generateShort()
            auto = True
        form = forms.URLSnipForm(data)
        if form.is_valid():
            inst = form.save()
            if auto:
                del data['alias']
                form = forms.URLSnipForm(data)
            base = request.build_absolute_uri("/")
            return render(request, 'home.html', {"form": form, "snippedurl": base+inst.alias, "name": inst.name})
        else:
            if auto:
                del data['alias']
                form = forms.URLSnipForm(data)
            return render(request, 'home.html', {"form": form, "errors": form.errors})
    else:
        form = forms.URLSnipForm()
    return render(request, 'home.html', {"form": form})


class ShortenURL(APIView):

    def get(self, request):
        s = ShortURL.objects.all()
        ser = ShortURLSerializer(s, many=True)
        return Response(ser.data)

    def post(self, request):
        data = request.data
        shorts = ShortURL.objects.all().values_list("alias")
        print(shorts)
        if data.get("alias"):
            short = data.get("alias")
            if (short,) in shorts:
                return HttpResponse("Alias Invalid", status=400)
        else:
            short = generateShort()
            while (short,) in shorts:
                short = generateShort()
        data["short"] = short
        print(data)
        url = data.get("url")
        name = data.get("name")
        serializer = ShortURLSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse(f"http://127.0.0.1:8000/infinitesimal/{short}")
        else:
            return Response(serializer.errors, status=400)
