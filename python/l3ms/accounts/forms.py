from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from models import UserProfile

class RetrieveUsernameForm(PasswordResetForm):
    def save(self):
        pass

class ResetPasswordForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            User.objects.get(username=username)
            return username
        except User.DoesNotExist:
            raise forms.ValidationError('That username does not exist.')

class RegistrationForm(forms.Form):
    first_name = forms.CharField(label='first name', max_length=30)
    last_name = forms.CharField(label='last name', max_length=30)
    username = forms.RegexField(label='username', max_length=30,
                                regex=r'^\w+$')
    email = forms.EmailField(label='email address')
    password1 = forms.CharField(label='password', max_length=128,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', max_length=128,
                                widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('A user with that username already exists.')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError('The password fields did not match.')
        return password2

    def save(self):
        u = User.objects.create_user(self.cleaned_data['username'],
                                     self.cleaned_data['email'],
                                     self.cleaned_data['password1'])
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.save()
        p = UserProfile(user=u)
        p.save()
        return u
