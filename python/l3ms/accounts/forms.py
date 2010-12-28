from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User

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

class RegistrationForm(UserCreationForm):
    first = forms.CharField(label="first name")
    email = forms.EmailField(label="email address", max_length=75)
