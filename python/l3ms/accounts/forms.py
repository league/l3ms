# l3ms.accounts.forms    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import loader, Context
from models import UserProfile
from strings import *

class EmailBaseForm(forms.Form):
    email = forms.EmailField(label=LABEL_EMAIL, max_length=75)

class RetrieveUsernameForm(EmailBaseForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            self.user = User.objects.get(email=email)
            return email
        except User.DoesNotExist:
            raise forms.ValidationError(M_EMAIL_UNKNOWN)

class ResetPasswordForm(forms.Form):
    username = forms.CharField(label=LABEL_USERNAME, max_length=30)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            self.user = User.objects.get(username=username)
            return username
        except User.DoesNotExist:
            raise forms.ValidationError(M_USERNAME_UNKNOWN)

class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set his/her password without
    entering the old password
    """
    new_password1 = forms.CharField(label=LABEL_PASSWORD_1,
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=LABEL_PASSWORD_2,
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(M_PASSWORDS_NEQ)
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

class EditProfileForm(forms.Form):
    last_name = forms.CharField(label=LABEL_LAST_NAME, max_length=30)
    first_name = forms.CharField(label=LABEL_FIRST_NAME, max_length=30)
    blurb = forms.CharField(label=LABEL_BLURB, widget=forms.Textarea,
                            required=False)

    def __init__(self, user, data=None, *args, **kwargs):
        self.user = user
        if not data:
            data = {}
        if 'first_name' not in data:
            data['first_name'] = user.first_name
        if 'last_name' not in data:
            data['last_name'] = user.last_name
        if 'blurb' not in data:
            data['blurb'] = user.get_profile().blurb
        super(EditProfileForm, self).__init__(data, *args, **kwargs)

    def save(self, commit=True):
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.get_profile().blurb = self.cleaned_data['blurb']
        if commit:
            self.user.save()
            self.user.get_profile().save()
        return self.user

class RegistrationForm(forms.Form):
    last_name = forms.CharField(label=LABEL_LAST_NAME, max_length=30)
    first_name = forms.CharField(label=LABEL_FIRST_NAME, max_length=30)
    email = forms.EmailField(label=LABEL_EMAIL)
    username = forms.RegexField(label=LABEL_USERNAME, max_length=30,
                                regex=r'^\w+$')
    password1 = forms.CharField(label=LABEL_PASSWORD_1, max_length=128,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=LABEL_PASSWORD_2, max_length=128,
                                widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(M_USERNAME_IN_USE)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(M_PASSWORDS_NEQ)
        return password2

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
            raise forms.ValidationError(M_EMAIL_IN_USE)
        except User.DoesNotExist:
            return email

    def save(self):
        self.user = User.objects.create_user(self.cleaned_data['username'],
                                             self.cleaned_data['email'],
                                             self.cleaned_data['password1'])
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.is_active = False
        self.user.save()
        return self.user
