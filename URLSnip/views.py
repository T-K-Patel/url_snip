import json
import time
from django.shortcuts import get_object_or_404, redirect, render
from . models import ShortURL
from django.contrib.auth import logout, login, authenticate
from .serializers import *
from .encryption import *
from urllib.parse import urlparse
from .tasks import sendOTP


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


def ForgotPassword(request):
    if request.user.is_authenticated:
        return redirect('/me/')
    e = request.GET.get('e', None)
    if request.method == 'POST':
        data = {"email": request.POST.get('email')}
        if data['email']:
            user = User.objects.filter(email=data['email']).first()
            if user is not None:
                if user.is_active:
                    otp = str(random.randint(100000, 999999))
                    validation = {"email": user.email,
                                  "timestamp": int(time.time()), "otp": otp, "key": generateShort(4), "rpfupass": generateShort(12)}
                    token = encrypt(json.dumps(validation))
                    sendOTP(request.build_absolute_uri("/"), user.email, user.username.capitalize(),
                            otp, validation["key"], token)

                    return redirect('/verify/?t=%s' % token, permanent=True)
                else:
                    return render(request, 'ForgotPassword.html', {"error": "Your account is not active."})
            else:
                return render(request, 'ForgotPassword.html', {"error": "Your account does not exist."})
        else:
            return render(request, 'ForgotPassword.html', {"error": "Please enter your email."})
    return render(request, 'ForgotPassword.html', {"e": e})


def VerifyEmail(request):
    if request.user.is_authenticated:
        return redirect('/me/')
    e = request.GET.get('e', None)
    token = request.GET.get('t', None)
    try:
        data = json.loads(decrypt(token))
        email = data['email']
        timestamp = int(data['timestamp'])
        otp_t = int(data['otp'])
        key = data['key']
        rpfupass = data['rpfupass']
    except:
        return redirect('/forgotpassword/?e=Invalid Verification Link. Get new one.', permanent=True)

    if timestamp < time.time()-300:
        return redirect("/forgotpassword/?e=Verification Link Has Expired. Get new one.", permanent=True)

    if request.method == 'POST':
        otp = ""
        for i in range(1, 7):
            otp += request.POST.get(f'otp{i}')
        if otp:
            otp = int(otp)
            user = User.objects.filter(email=email).first()
            if user is not None:
                if otp == otp_t:
                    token = {"username": user.username, "rpfupass": rpfupass}
                    rpfuwoptoken = encrypt(json.dumps(token))
                    user.set_password(rpfupass)
                    user.save()
                    return redirect("/resetpassword/?op=%s" % rpfuwoptoken, permanent=True)
                else:
                    return redirect(f"/verify/?t={token}&e=Invalid otp.", permanent=True)
            else:
                return redirect(f"/verify/?t={token}&e=Invalid User.", permanent=True)
        else:
            return redirect(f"/verify/?t={token}&e=Please enter otp.", permanent=True)
    return render(request, 'Verify.html', {"email": email, "key": key, "error": e, "token": token})


def ResetPasssword(request):
    op = request.GET.get('op', None)
    if request.user.is_authenticated:
        op = None
        opass = None

    if op:
        try:
            rpfuwoptoken = json.loads(decrypt(op))
            opass = rpfuwoptoken['rpfupass']
            username = rpfuwoptoken['username']
        except:
            return redirect('/resetpassword/', permanent=True)
        user = User.objects.filter(username=username).first()
        if not user.check_password(opass):
            return redirect('/forgotpassword/?e=Invalid Reset Password Link', permanent=True)

    elif not request.user.is_authenticated:
        return redirect('/forgotpassword/?e=Cannot reset password.', permanent=True)
    else:
        user = request.user

    if request.method == 'POST':
        opass = opass or request.POST.get('opassword', None)
        if not opass:
            return render(request, 'ResetPassword.html', {"op": op, "error": "Enter Old Password"})
        if not user.check_password(opass):
            return render(request, 'ResetPassword.html', {"op": op, "error": "Invalid Old Password."})

        if opass is None and request.POST.get('opassword'):
            opass = request.POST.get('opassword', None)

        data = {"password": request.POST.get(
            'password'), "cpassword": request.POST.get('cpassword')}

        if not data['password']:
            return render(request, 'ResetPassword.html', {"op": op, "error": "Please enter password."})

        if data['cpassword'] != data['password']:
            return render(request, 'ResetPassword.html', {"op": op, "error": "Password must match."})

        if len(data['password']) < 6:
            return render(request, 'ResetPassword.html', {"op": op, "error": "Password must contain atleast 6 characters."})

        if user is not None:
            if user.is_active:
                user.set_password(data['password'])
                user.save()
                if request.user.is_authenticated:
                    request.session['session_pass_key'] = encrypt(
                        user.password)
                    return redirect('/me/', permanent=True)
                return redirect('/login/', permanent=True)
                # return render(request, 'ResetPassword.html', {"success": "Your password has been changed."})
            else:
                return render(request, 'ResetPassword.html', {"op": op, "error": "Your account is not active."})
        else:
            return render(request, 'ResetPassword.html', {"op": op, "error": "Your account does not exist."})

    return render(request, 'ResetPassword.html', {"op": op})


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
    e = request.GET.get('e', None)
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            request.session['session_pass_key'] = encrypt(user.password)
            login(request, user)
            return redirect(request.GET.get("next") or "/")
        else:
            return render(request, 'login.html', {"username": username, "error": "Invalid Username or password. (Both fields are case sensitive)"})
    else:
        return render(request, 'login.html', {'error': e})


def Logout(request):
    logout(request)
    return redirect("/")


# def Demo(request):
#     request.session['session_pass_key'] = "hellohghkfgsbb"
#     return render(request, 'home.html')
