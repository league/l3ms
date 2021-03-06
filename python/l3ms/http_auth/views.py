# l3ms.http_auth.views    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.http import urlquote
import base64

SESSION_LOGOUT = 'logout'
SESSION_NEXT_PAGE = 'next'
SESSION_MESSAGE = 'message'

M_AUTH_REQUIRED = """Authentication is required.  Please log in or
register as a new user.  If you recently registered, you must first
check your email and use the validation link."""

M_LOGGED_OUT = """You have logged out."""

def render(template, request, message=''):
    d = {'message': message,
         'user': request.user,
         'site_name': settings.SITE_NAME,
         }
    if settings.HTTP_AUTH_DEBUG:
        template = 'http-auth/test.html'
        d['request'] = request
    return render_to_response(template, d)

def options(request, message=''):
    if SESSION_MESSAGE in request.session:
        message = request.session[SESSION_MESSAGE]
        del request.session[SESSION_MESSAGE]
    return render('http-auth/options.html', request, message)

def check_login(request):
    if 'HTTP_AUTHORIZATION' not in request.META:
        return False
    kind, cred = request.META['HTTP_AUTHORIZATION'].split()
    assert kind.lower() == 'basic'
    name, pwd = base64.b64decode(cred).split(':')
    user = auth.authenticate(username=name, password=pwd)
    if user is None or not user.is_active:
        return False
    if SESSION_LOGOUT in request.session:
        if request.session[SESSION_LOGOUT] == user.username:
            return False
    return user

def login(request):
    user = check_login(request)
    if not user:
        return force(request)
    if SESSION_NEXT_PAGE in request.session:
        next = request.session[SESSION_NEXT_PAGE]
        del request.session[SESSION_NEXT_PAGE]
    else:
        next = reverse('home')
    auth.login(request, user)
    return HttpResponseRedirect(next)

def force(request):
    if SESSION_LOGOUT in request.session:
        del request.session[SESSION_LOGOUT]
        request.session.set_expiry(None) # back to global default
    r = options(request,  # could be more helpful if not is_active
                message=M_AUTH_REQUIRED)
    r.status_code = 401
    r['WWW-Authenticate'] = 'Basic realm="%s"' % settings.HTTP_AUTH_REALM
    return r

def logout(request):
    if request.user.is_authenticated():
        u = request.user.username
        auth.logout(request)
        request.session[SESSION_LOGOUT] = u
        request.session.set_expiry(0) # upon closing web browser
        request.session[SESSION_MESSAGE] = M_LOGGED_OUT
    return HttpResponseRedirect(reverse('auth_options'))

def login_required(f):
    def do_it(request, *args, **kwargs):
        if request.user.is_authenticated():
            return f(request, *args, **kwargs)
        else:
            request.session[SESSION_NEXT_PAGE] = \
                urlquote(request.get_full_path())
            request.session.set_expiry(0) # upon closing web browser
            return HttpResponseRedirect(reverse('auth_options'))
    return do_it

@login_required
def test(request):
    return render('http-auth/test.html', request,
                  message='This was to be secret!')
