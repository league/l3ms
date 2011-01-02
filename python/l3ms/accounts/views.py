from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from forms import *
from l3ms.http_auth.views import login_required
from models import *

@login_required
def home(request):
    return profile(request, username=request.user.username)

@login_required
def profile(request, username):
    try:
        if request.user.username == username:
            d = {'user': request.user, 'privileged': True}
        else:
            d = {'user': User.objects.get(username=username),
                 'privileged': request.user.is_staff}
    except User.DoesNotExist:
        raise Http404
    return render_to_response('profile.html', d)

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
            request.session['message'] = \
                'Your user name has been set by email.'
            return HttpResponseRedirect(url)
    else:
        form = RetrieveUsernameForm()
    return render_to_response('acct/retrieve.html', {'form': form})

def login_page(auth_form=None, retrieve_form=None,
               reset_form=None, new_form=None, next=None):
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
                               'new_form': new_form,
                               'next': next})

def forgot_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if not form.is_valid():
            return login_page(reset_form = form)
        u = User.objects.get(username=form.cleaned_data['username'])
        k = ActivationKey.objects.create(u, RESET_PASSWORD, u.email)
        return HttpResponse('<a href="%s">reset link</a> <a href="%s">home</a>'
                            % (k.get_absolute_url(), reverse('home')))
    return HttpResponseRedirect(reverse('home'))

def activate(request, key):
    try:
        k = ActivationKey.objects.get(key=key)
    except ActivationKey.DoesNotExist:
        raise Http404
    if k.action == VALIDATE_EMAIL:
        u = k.user
        u.get_profile().save_validated_email(k.email)
        k.delete()
        return render_to_response('thanks-email.html', {'user': u})
    return HttpResponse(str(k))

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

