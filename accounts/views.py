from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from forms import *

def home(request):
    if request.user.is_authenticated():
        return profile(request, username=request.user.username)
    else:
        return login_page()

def login_page(auth_form=None, retrieve_form=None,
               reset_form=None, new_form=None):
    if not auth_form:
        auth_form = AuthenticationForm()
    if not retrieve_form:
        retrieve_form = RetrieveUsernameForm()
    if not reset_form:
        reset_form = ResetPasswordForm()
    if not new_form:
        new_form = RegistrationForm()
    return render_to_response('login-or-register.html',
                              {'auth_form': auth_form,
                               'retrieve_form': retrieve_form,
                               'reset_form': reset_form,
                               'new_form': new_form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(None, request.POST)
        if not form.is_valid():
            return login_page(auth_form = form)
        auth.login(request, form.get_user())
    return HttpResponseRedirect(reverse('home'))

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')

def forgot_username(request):
    if request.method == 'POST':
        form = RetrieveUsernameForm(request.POST)
        if not form.is_valid():
            return login_page(retrieve_form = form)
        email = form.cleaned_data['email']
        users = User.objects.filter(email__iexact = email)
        return HttpResponse('%s = %s<br><a href="%s">home</a>' %
                            (email, users[0].username, reverse('home')))
    return HttpResponseRedirect(reverse('home'))

def forgot_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if not form.is_valid():
            return login_page(reset_form = form)
        return HttpResponse('can reset '+str(form.cleaned_data['username']))
    return HttpResponseRedirect(reverse('home'))

def register(request):
    return HttpResponse('not implemented')

def edit_email(request):
    return HttpResponse('not implemented')

def edit_profile(request):
    return HttpResponse('not implemented')

@login_required
def profile(request, username=None):
    buf = ('Hello %s, <a href="%s">log out</a>' %
           (username, reverse('logout')))
    if request.user.is_staff:
        buf += '<br><a href="%s">admin</a>' % reverse('admin:index')
    return HttpResponse(buf)

def navbar(request):
    return HttpResponse('not implemented')

