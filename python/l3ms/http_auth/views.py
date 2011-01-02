from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.http import urlquote
from settings import HTTP_AUTH_REALM, HTTP_AUTH_DEBUG
import base64

def render(template, request, message='', next=''):
    d = {'message': message,
         'next': next,
         'user': request.user
         }
    if HTTP_AUTH_DEBUG:
        template = 'http-auth/test.html'
        d['request'] = request
    return render_to_response(template, d)

def options(request, message='', next=''):
    next = request.GET.get('next', next)
    return render('http-auth/options.html', request, message, next)

def login(request, next=''):
    next = request.GET.get('next', next)
    try:
        kind, cred = request.META['HTTP_AUTHORIZATION'].split()
        assert kind.lower() == 'basic'
        name, pwd = base64.b64decode(cred).split(':')
        user = auth.authenticate(username=name, password=pwd)
        if user is None:
            return force(request, next)
        if request.session.get('logout', None) == user.username:
            del request.session['logout']
            request.session.set_expiry(None) # use global default
            return force(request, next)
        auth.login(request, user)
        return (HttpResponseRedirect(next) if next else
                render('http-auth/login.html', request))
    except KeyError:
        return force(request, next)

def force(request, next):
    r = options(request,
                message='Authentication is required.',
                next=next)
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
    def do_it(request):
        if request.user.is_authenticated():
            return f(request)
        else:
            dest = reverse('auth_options')
            next = urlquote(request.get_full_path())
            return HttpResponseRedirect('%s?next=%s' % (dest, next))
    return do_it

@login_required
def test(request):
    return render('http-auth/test.html', request,
                  message='This was to be secret!')