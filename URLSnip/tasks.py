
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
try:
    from url_snip.settings import EMAIL_HOST_USER
except:
    EMAIL_HOST_USER = "noreply.projekt.x.team@gmail.com"


def sendRegMail(base, email, username, link):
    context = {
        "base": base,
        "username": username,
        "link": link
    }
    html_content = render_to_string(
        'Mail/RegistrationMail.html', context=context)
    text_content = strip_tags(html_content)
    return send_mail(
        subject="URL Snip Account Registration",
        from_email=f"URL Snip Team <{EMAIL_HOST_USER}>",
        message=text_content,
        recipient_list=[email],
        html_message=html_content,
        fail_silently=True
    )


def sendOTP(url, email, name, otp, key, token):
    context = {
        "name": name,
        "base": url,
        "otp": otp,
        "key": key,
        "token": token
    }
    html_content = render_to_string(
        'Mail/Mail.html', context=context)
    text_content = strip_tags(html_content)
    return send_mail(
        subject="OTP for URL Snip Account Password Reset",
        from_email=f"URL Snip Team <{EMAIL_HOST_USER}>",
        message=text_content,
        recipient_list=[email],
        html_message=html_content,
        fail_silently=True
    )
