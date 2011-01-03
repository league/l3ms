from django.contrib import auth
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from forms import *
from l3ms.email_validation.models import ValidationKey
from l3ms.http_auth.views import login_required, SESSION_MESSAGE
from models import *

@login_required
def home(request):
    return profile(request, username=request.user.username)

@login_required
def profile(request, username):
    if request.user.username == username:
        user = request.user
        privileged = True
    else:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        privileged = request.user.is_staff
    gravatar = gravatar_url(user)
    return render_to_response('profile.html',
                              {'user': user, 'privileged': privileged,
                               'gravatar': gravatar})

ACCT_NAME_SENT = 'Your user name has been set by email.'
ACCT_LINK_SENT = 'A password reset link has been set by email.'
ACCT_PASS_CHANGED = 'Your password has been changed.'

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

def edit_email(request):
    return HttpResponse('not implemented')

def edit_profile(request):
    return HttpResponse('not implemented')


## this should really be moved to courses app
def navbar(request, path):
    return HttpResponse('not implemented: '+path)

