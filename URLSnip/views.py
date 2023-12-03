from django.http import HttpResponse
from django.utils import timezone
import json
import time
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from . models import ShortURL
from django.contrib.auth import logout, login, authenticate
from .serializers import *
from .encryption import *
from urllib.parse import urlparse
from .tasks import sendOTP, sendRegMail
from django.contrib.auth.decorators import user_passes_test


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
        return redirect('/me')
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

                    return redirect('/verify?t=%s' % token, permanent=True)
                else:
                    return render(request, 'ForgotPassword.html', {"error": "Your account is not active."})
            else:
                return render(request, 'ForgotPassword.html', {"error": "Your account does not exist."})
        else:
            return render(request, 'ForgotPassword.html', {"error": "Please enter your email."})
    return render(request, 'ForgotPassword.html', {"e": e})


def VerifyEmail(request):
    if request.user.is_authenticated:
        return redirect('/me')
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
        return redirect('/forgotpassword?e=Invalid Verification Link. Get new one.', permanent=True)

    if timestamp < time.time()-300:
        return redirect("/forgotpassword?e=Verification Link Has Expired. Get new one.", permanent=True)

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
                    return redirect("/resetpassword?op=%s" % rpfuwoptoken, permanent=True)
                else:
                    return redirect(f"/verify?t={token}&e=Invalid otp.", permanent=True)
            else:
                return redirect(f"/verify?t={token}&e=Invalid User.", permanent=True)
        else:
            return redirect(f"/verify?t={token}&e=Please enter otp.", permanent=True)
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
            return redirect('/forgotpassword?e=Invalid Reset Password Link', permanent=True)

    elif not request.user.is_authenticated:
        return redirect('/forgotpassword?e=Cannot reset password.', permanent=True)
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
                    return redirect('/me', permanent=True)
                return redirect('/login', permanent=True)
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
        return redirect('/login?next=/me')
    urls = []
    host = request.build_absolute_uri("/")
    if request.user.is_authenticated:
        t = ShortURL.objects.filter(user=request.user).order_by("-created")
        urls = ShortURLSerializer(t, many=True).data
    return render(request, 'Profile.html', {'urls': urls, "host": host})


def App(request):
    if not request.user.is_authenticated:
        return redirect('/login?next=/app')
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


def Register(request):
    messages = []
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        data = {"username": username, "email": email}
        user_lst = User.objects.filter(
            Q(username=username) | Q(email=email))
        user = user_lst.filter(is_active=True).first()
        user_ina = user_lst.filter(is_active=False)
        start_date = timezone.now() - timezone.timedelta(minutes=15)
        if len(username) < 5:
            messages += ["Username must contain atleast 5 characters."]
        elif not username.isalpha():
            messages += ["Username must contain only letters."]
        elif user:
            messages += ["User with this username or email already exists."]
        elif user_ina.filter(date_joined__gt=start_date).exists():
            messages += ["Wait 15 minutes before trying again."]
        else:
            for u in user_ina.filter(date_joined__lt=start_date):
                u.delete()

        if not password:
            messages += ["Please enter password."]
        elif len(password) < 6:
            messages += ["Password must contain atleast 6 characters."]
        elif password != cpassword:
            messages += ["Confirm Pasword does not match."]
        success = None
        if not messages:
            user = User.objects.create_user(
                username=username, email=email, is_active=False)
            user.save()
            messages = []
            token = encrypt(json.dumps(
                {"username": username, "exp": time.time()+15*60}))
            sendRegMail(request.build_absolute_uri(
                '/'), email, username, token)
            success = "Your account has been created. Verify your account by visiting link sent to your mail."
            data = None
        return render(request, 'Register.html', {"messages": messages, "data": data, "success": success}, status=(400 if messages else 200))
    else:
        return render(request, 'Register.html', {"messages": messages})


def Activate(request, token):
    try:
        data = json.loads(decrypt(token))
        if data['exp'] <= time.time():
            raise Exception("Invalid Link")
        user = User.objects.get(username=data['username'])
        if user.is_active:
            raise Exception("Invalid Link")
        user.is_active = True
        user.save()
        return HttpResponse("<center><h1>Your Account has been activated.</h1></center>")
    except:
        return HttpResponse("<center><h1>Invalid Link.</h1></center>",status=400)


def Login(request):
    e = request.GET.get('e', None)
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        u = User.objects.get(username=username)
        if u:
            print(u.check_password(password))
        else:
            print("No user.")
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

@user_passes_test(lambda u: u.is_superuser,'login')
def clean_users(req):
    users = User.objects.filter(is_active=False,date_joined__lt=(timezone.now() - timezone.timedelta(minutes=16)))
    for u in users:
        u.delete()
    return HttpResponse("<center><h1>All Inactive Users Deleted.</h1></center>")