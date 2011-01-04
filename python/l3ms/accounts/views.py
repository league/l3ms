# l3ms.accounts.views    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django import http, template
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from hashlib import md5
from l3ms.email_validation.models import ValidationKey
from l3ms.http_auth.views import login_required, SESSION_MESSAGE
from strings import *
import forms

def reverse_u(view, username):
    return reverse(view, kwargs={'username': username})

def profile_of(user):
    return reverse_u('profile', user.username)

def is_privileged(request, username):
    return request.user.is_staff or request.user.username == username

def get_username_or_404(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

def gravatar_url(request, user):
    h = md5(user.email.lower()).hexdigest()
    d = 'https://secure' if request.is_secure() else 'http://www'
    return ('%s.gravatar.com/avatar/%s.jpg?d=%s' %
            (d, h, settings.GRAVATAR_FALLBACK))

@login_required
def home(request):
    return profile(request, username=request.user.username)

@login_required
def profile(request, username):
    profile_user = get_username_or_404(username)
    message = request.session.get(SESSION_MESSAGE, '')
    if message:
        del request.session[SESSION_MESSAGE]
    # Maintain the convention that {{user}} always refers to the
    # requesting user; so here {{profile}} is the user to display.
    return render_to_response('profile.html',
                              {'user': request.user,
                               'profile': profile_user,
                               'privileged': is_privileged(request, username),
                               'message': message,
                               'gravatar': gravatar_url(request, profile_user)})


def auth_redirect(request, message):
    request.session[SESSION_MESSAGE] = message
    return http.HttpResponseRedirect(reverse('auth_options'))

def forgot_username(request):
    if request.method == 'POST':
        form = forms.RetrieveUsernameForm(request.POST)
        if form.is_valid():
            url = request.build_absolute_uri(reverse('auth_options'))
            t = template.loader.get_template('email/retrieve.txt')
            c = template.Context({'username': form.user.username,
                                  'site_name': settings.SITE_NAME,
                                  'auth_url': url})
            send_mail(SUBJ_RETRIEVE_USERNAME % settings.SITE_NAME,
                      t.render(c),
                      settings.FROM_EMAIL,
                      [form.cleaned_data['email']])
            return auth_redirect(request, M_USERNAME_SENT)
    else:
        form = forms.RetrieveUsernameForm()
    return render_to_response('acct/retrieve.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            ValidationKey.objects.create(request.build_absolute_uri,
                                         form.user.email,
                                         form.user, 'P')
            return auth_redirect(request, M_PASSWORD_SENT)
    else:
        form = forms.ResetPasswordForm()
    return render_to_response('acct/reset.html', {'form': form})

def forgot_password_handler(request, k):
    if request.method == 'POST':
        form = forms.SetPasswordForm(k.user, request.POST)
        if form.is_valid():
            form.save()
            k.delete()
            return auth_redirect(request, M_PASSWORD_CHANGED)
    else:
        form = forms.SetPasswordForm(k.user)
    url = request.get_full_path()
    return render_to_response('acct/reset2.html',
                              {'form': form, 'url': url})

ValidationKey.objects.register(
    'P', 'password reset', 'email/reset.txt',
    forgot_password_handler, 96)

def edit_email(request, username):
    if not is_privileged(request, username):
        return http.HttpResponseForbidden('forbidden')
    profile_user = get_username_or_404(username)
    if request.method == 'POST':
        form = forms.EmailBaseForm(request.POST)
        if form.is_valid():
            if request.user.is_staff: # just do it right away
                profile_user.email = form.cleaned_data['email']
                profile_user.save()
                request.session[SESSION_MESSAGE] = M_EMAIL_CHANGED
            else:
                ValidationKey.objects.create(request.build_absolute_uri,
                                             form.cleaned_data['email'],
                                             profile_user, 'E')
                request.session[SESSION_MESSAGE] = M_EMAIL_SENT
            return http.HttpResponseRedirect(profile_of(profile_user))
    else:
        form = forms.EmailBaseForm()
    return render_to_response('acct/edit-email.html',
                              {'profile': profile_user,
                               'form': form,
                               'action': request.get_full_path()})

def edit_email_handler(request, k):
    k.user.email = k.email
    k.user.save()
    request.session[SESSION_MESSAGE] = M_EMAIL_CHANGED
    return http.HttpResponseRedirect(profile_of(k.user))

ValidationKey.objects.register(
    'E', 'email address change', 'email/edit-email.txt',
    edit_email_handler, 96)

def edit_password(request, username):
    if not is_privileged(request, username):
        return http.HttpResponseForbidden('forbidden')
    profile_user = get_username_or_404(username)
    if request.method == 'POST':
        form = forms.PasswordChangeForm(profile_user, request.POST)
        if form.is_valid():
            form.save()
            request.session[SESSION_MESSAGE] = M_PASSWORD_CHANGED
            return http.HttpResponseRedirect(profile_of(profile_user))
    else:
        form = forms.PasswordChangeForm(profile_user)
    return render_to_response('acct/edit-password.html',
                              {'profile': profile_user,
                               'form': form,
                               'action': request.get_full_path()})

def register(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            ValidationKey.objects.create(request.build_absolute_uri,
                                         form.cleaned_data['email'],
                                         form.user, 'N')
            return auth_redirect(request, M_NEW_USER_SENT)
    else:
        form = forms.RegistrationForm()
    return render_to_response('acct/register.html',
                              {'form': form,
                               'action': request.get_full_path()})

def new_account_handler(request, k):
    u = k.user
    u.is_active = True
    u.save()
    k.delete()
    request.session[SESSION_MESSAGE] = M_ACTIVATED
    return http.HttpResponseRedirect(profile_of(u))

ValidationKey.objects.register(
    'N', 'account', 'email/new.txt',
    new_account_handler, 96)

def edit_profile(request):
    return http.HttpResponse('not implemented')


## this should really be moved to courses app
def navbar(request, path):
    return http.HttpResponse('not implemented: '+path)

