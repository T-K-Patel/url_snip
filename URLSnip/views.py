import datetime
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from . models import ShortURL
from django.contrib.auth import logout, login, authenticate
from .serializers import *
from urllib.parse import urlparse, urljoin


def getHost(url):
    u = urlparse(url)
    return u.scheme + "://" + u.hostname


def getDomain(url):
    u = urlparse(url)
    d = u.hostname
    if u.port:
        d += f":{u.port}"
    return d


def GetShort(request, url):
    url = get_object_or_404(ShortURL, alias=url)
    url.save()
    return redirect(url.url)


def LoadTemp(request):
    urls = []
    host = request.build_absolute_uri("/")
    if request.user.is_authenticated:
        t = ShortURL.objects.filter(user=request.user).order_by("-created")
        urls = ShortURLSerializer(t).data
    return render(request, 'url_short_form.html', {'owened': urls, 'host': host})


def Home(request):
    return render(request, 'home.html')


def Profile(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=/me/')
    urls = []
    host = request.build_absolute_uri("/")
    if request.user.is_authenticated:
        t = ShortURL.objects.filter(user=request.user).order_by("-created")
        urls = ShortURLSerializer(t, many=True).data
    return render(request, 'Profile.html', {'urls': urls, "host": host})


def App(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=/app/')
    urls = []
    host = request.build_absolute_uri("/")
    if request.user.is_authenticated:
        t = ShortURL.objects.filter(user=request.user).order_by("-created")
        urls = ShortURLSerializer(t, many=True).data

    if request.method == "POST":
        data = {"alias": request.POST.get('alias'),
                "url": request.POST.get('url'), "user": request.user.pk}
        auto = False
        if data['url'] and getHost(data['url']) == getHost(host) and urlparse(data['url']).port == urlparse(host).port:
            return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host, 'data': data, "error": {"url": "Invalid Url"}}, status=400)
        if not data['alias']:
            n = t.filter(url=data['url']).first()
            if n:
                data['alias'] = n.alias
                data['created'] = getDelay(n.created)
                return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host, 'data': data})
            data['alias'] = generateShort()
            auto = True
        serializer = ShortURLSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            data['created'] = "just now"
            urls.insert(0, data)
            return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host, "data": data})
        else:
            print(serializer.errors)
            if auto and serializer.errors.get('alias'):
                data['alias'] = generateShort()
                serializer = ShortURLSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    data['created'] = "just now"
                    urls.insert(0, data)
                    return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host, "data": data})
                else:
                    if auto:
                        data['alias'] = ""
                    return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host, "data": data, "error": {"other": "Some error occured"}}, status=500)

            if not auto and serializer.errors.get('alias'):
                if serializer.errors['alias'] == "reserved":
                    error = "Can't use reserved keys."
                else:
                    error = "Invalid key."
                if auto:
                    data['alias'] = ""
                return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host, 'data': data, "error": {"alias": error}}, status=400)
            if auto:
                data['alias'] = ""
            error = {"url": "Invalid Url"}if serializer.errors['url'] else {
                "other": "Some error occured"}
            return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host, 'data': data, "error": error}, status=400)

    return render(request, 'url_short_form.html', {'urls': urls, "domain": getDomain(host), 'host': host})


def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next") or "/")
        else:
            return render(request, 'login.html', {"username": username, "error": "Invalid Username or password. (Both fields are case sensitive)"})
    else:
        return render(request, 'login.html')


def Logout(request):
    logout(request)
    return redirect("/")
