from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from URLSnip.encryption import decrypt


class InvalidateSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        super().process_request(request)

        # Check if the user's password has changed
        if request.user.is_authenticated:
            user_key = request.user.password
            _session_key = request.session.get('session_pass_key', None)
            try:
                session_key = decrypt(_session_key)
            except:
                request.session.flush()
                return HttpResponseRedirect('/login/?e=Your session has expired or Password was reset. Login again to continue.')
            if user_key and session_key and user_key != session_key:
                request.session.flush()
                return HttpResponseRedirect('/login/?e=Your session has expired or Password was reset. Login again to continue.')
