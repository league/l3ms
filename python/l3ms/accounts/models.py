from base64 import urlsafe_b64encode
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from hashlib import md5
from random import random

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    is_email_valid = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.user)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', (), {'username': self.user.username})

    def save_validated_email(self, email):
        self.user.email = email
        self.is_email_valid = True
        self.user.save()
        self.save()

    def is_complete(self):
        return bool(self.user.username and self.user.first_name and
                    self.user.last_name and self.user.email and
                    self.user.has_usable_password())

RESET_PASSWORD = 'R'
VALIDATE_EMAIL = 'E'
INVITE_USER = 'I'

class ActivationManager(models.Manager):
    def create(self, user, action, email):
        r = email + random().hex()
        k = urlsafe_b64encode(md5(r).digest()[1:])
        ak = self.model(key=k, action=action, user=user, email=email)
        # send email here too?
        ak.save()
        return ak

class ActivationKey(models.Model):
    key = models.CharField(max_length=20, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=1, choices=(
            (RESET_PASSWORD, 'Reset password'),
            (VALIDATE_EMAIL, 'Validate email'),
            (INVITE_USER, 'Invite user')
            ))
    user = models.ForeignKey(User)
    email = models.EmailField()

    objects = ActivationManager()

    def __unicode__(self):
        return '%s %s %s' % (
            self.get_action_display(),
            self.email,
            self.key
            )

    @models.permalink
    def get_absolute_url(self):
        return ('activate', (), {'key': self.key})

admin.site.register(UserProfile)
admin.site.register(ActivationKey)
