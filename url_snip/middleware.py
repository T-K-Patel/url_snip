import time
import json
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
                session_data = json.loads(decrypt(_session_key))
                session_key = session_data['pass']
                lg_time = session_data['login_time']
                if lg_time + 10*24*3600 < time.time():
                    request.session.flush()
                    return HttpResponseRedirect('/login?e=Your session has expired. Login again to continue.')
            except:
                request.session.flush()
                return HttpResponseRedirect('/login?e=Your session has expired or Password was reset. Login again to continue.')

            if user_key and session_key and user_key != session_key:
                request.session.flush()
                return HttpResponseRedirect('/login?e=Your Password was reset. Login again to continue.')
