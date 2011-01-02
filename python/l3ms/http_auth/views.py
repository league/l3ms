from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.http import urlquote
from settings import HTTP_AUTH_REALM, HTTP_AUTH_DEBUG
import base64

def render(template, request, message=''):
    d = {'message': message,
         'user': request.user,
         }
    if HTTP_AUTH_DEBUG:
        template = 'http-auth/test.html'
        d['request'] = request
    return render_to_response(template, d)

def options(request, message=''):
    return render('http-auth/options.html', request, message)

def login(request):
    try:
        kind, cred = request.META['HTTP_AUTHORIZATION'].split()
        assert kind.lower() == 'basic'
        name, pwd = base64.b64decode(cred).split(':')
        user = auth.authenticate(username=name, password=pwd)
        if user is None:
            return force(request)
        if request.session.get('logout', None) == user.username:
            del request.session['logout']
            request.session.set_expiry(None) # use global default
            return force(request)
        next = request.session.get('next', '')
        del request.session['next']
        auth.login(request, user)
        return (HttpResponseRedirect(next) if next else
                render('http-auth/login.html', request))
    except KeyError:
        return force(request)

def force(request):
    r = options(request,
                message='Authentication is required.')
    r.status_code = 401
    r['WWW-Authenticate'] = 'Basic realm="%s"' % HTTP_AUTH_REALM
    return r

def logout(request):
    if request.user.is_authenticated():
        u = request.user.username
        auth.logout(request)
        request.session['logout'] = u
        request.session.set_expiry(0) # upon closing web browser
    return render('http-auth/logout.html', request)

def login_required(f):
    def do_it(request, *args, **kwargs):
        if request.user.is_authenticated():
            return f(request, *args, **kwargs)
        else:
            request.session['next'] = urlquote(request.get_full_path())
            request.session.set_expiry(0) # upon closing web browser
            return HttpResponseRedirect(reverse('auth_options'))
    return do_it

@login_required
def test(request):
    return render('http-auth/test.html', request,
                  message='This was to be secret!')
