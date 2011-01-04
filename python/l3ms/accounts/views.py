# l3ms.accounts.views    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib import auth
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import *
from django.shortcuts import render_to_response
from forms import *
from l3ms.email_validation.models import ValidationKey
from l3ms.http_auth.views import login_required, SESSION_MESSAGE
from models import *

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
                               'gravatar': gravatar_url(profile_user)})

ACCT_NAME_SENT = 'Your user name has been sent by email.'
ACCT_LINK_SENT = 'A password reset link has been sent by email.'
ACCT_PASS_CHANGED = 'Your password has been changed.'
ACCT_MAIL_SENT = 'A validation link has been sent to your new address.'
ACCT_MAIL_CHANGED = 'Your email address has been changed.'

def auth_redirect(request, message):
    request.session[SESSION_MESSAGE] = message
    return HttpResponseRedirect(reverse('auth_options'))

def forgot_username(request):
    if request.method == 'POST':
        form = RetrieveUsernameForm(request.POST)
        if form.is_valid():
            url = request.build_absolute_uri(reverse('auth_options'))
            t = loader.get_template('email/retrieve.txt')
            c = Context({'username': form.user.username,
                         'site_name': SITE_NAME,
                         'auth_url': url})
            send_mail(SITE_NAME+' user name', t.render(c),
                      FROM_EMAIL, [form.cleaned_data['email']])
            return auth_redirect(request, ACCT_NAME_SENT)
    else:
        form = RetrieveUsernameForm()
    return render_to_response('acct/retrieve.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            ValidationKey.objects.create(request.build_absolute_uri,
                                         form.user.email,
                                         form.user, 'P')
            return auth_redirect(request, ACCT_LINK_SENT)
    else:
        form = ResetPasswordForm()
    return render_to_response('acct/reset.html', {'form': form})

def forgot_password_handler(request, k):
    if request.method == 'POST':
        form = SetPasswordForm(k.user, request.POST)
        if form.is_valid():
            form.save()
            k.delete()
            return auth_redirect(request, ACCT_PASS_CHANGED)
    else:
        form = SetPasswordForm(k.user)
    url = request.get_full_path()
    return render_to_response('acct/reset2.html',
                              {'form': form, 'url': url})

ValidationKey.objects.register(
    'P', 'password reset', 'email/reset.txt',
    forgot_password_handler, 96)

def edit_email(request, username):
    if not is_privileged(request, username):
        return HttpResponseForbidden('forbidden')
    profile_user = get_username_or_404(username)
    if request.method == 'POST':
        form = EmailBaseForm(request.POST)
        if form.is_valid():
            if request.user.is_staff: # just do it right away
                profile_user.email = form.cleaned_data['email']
                profile_user.save()
                request.session[SESSION_MESSAGE] = ACCT_MAIL_CHANGED
            else:
                ValidationKey.objects.create(request.build_absolute_uri,
                                             form.cleaned_data['email'],
                                             profile_user, 'E')
                request.session[SESSION_MESSAGE] = ACCT_MAIL_SENT
            return HttpResponseRedirect(profile_of(profile_user))
    else:
        form = EmailBaseForm()
    return render_to_response('acct/edit-email.html',
                              {'profile': profile_user,
                               'form': form,
                               'action': request.get_full_path()})

def edit_email_handler(request, k):
    k.user.email = k.email
    k.user.save()
    request.session[SESSION_MESSAGE] = ACCT_MAIL_CHANGED
    return HttpResponseRedirect(profile_of(k.user))

ValidationKey.objects.register(
    'E', 'email address change', 'email/edit-email.txt',
    edit_email_handler, 96)

def edit_password(request, username):
    if not is_privileged(request, username):
        return HttpResponseForbidden('forbidden')
    profile_user = get_username_or_404(username)
    if request.method == 'POST':
        form = PasswordChangeForm(profile_user, request.POST)
        if form.is_valid():
            form.save()
            request.session[SESSION_MESSAGE] = ACCT_PASS_CHANGED
            return HttpResponseRedirect(profile_of(profile_user))
    else:
        form = PasswordChangeForm(profile_user)
    return render_to_response('acct/edit-password.html',
                              {'profile': profile_user,
                               'form': form,
                               'action': request.get_full_path()})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if not form.is_valid():
            return login_page(new_form = form)
        form.save()
        u = auth.authenticate(username=form.cleaned_data['username'],
                              password=form.cleaned_data['password1'])
        k = ActivationKey.objects.create(u, VALIDATE_EMAIL, u.email)
        url = request.build_absolute_uri(k.get_absolute_url())
        u.email_user('validate', url)
        auth.login(request, u)
    return HttpResponseRedirect(reverse('home'))

def edit_profile(request):
    return HttpResponse('not implemented')


## this should really be moved to courses app
def navbar(request, path):
    return HttpResponse('not implemented: '+path)

