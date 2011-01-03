from base64 import urlsafe_b64encode
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from hashlib import md5
from random import random

def gravatar_url(user):
    h = md5(user.email.lower()).hexdigest()
    return 'https://secure.gravatar.com/avatar/%s.jpg?d=retro' % h

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

admin.site.register(UserProfile)
