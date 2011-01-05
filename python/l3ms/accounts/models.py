# l3ms.accounts.models    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from base64 import urlsafe_b64encode
from django.contrib.auth.models import User
from django.db import models
from hashlib import md5
from random import random

# Duck-punch a gravatar method into User class, so we can easily
# retrieve it from templates.

GRAVATAR_HTTPS = True
GRAVATAR_DEFAULT = 'retro'

def gravatar(self, size=80, default=GRAVATAR_DEFAULT):
    h = md5(self.email.lower()).hexdigest()
    return('%s.gravatar.com/avatar/%s.jpg?s=%d&d=%s' %
           ('https://secure' if GRAVATAR_HTTPS else 'http://www',
            h, size, default))
User.gravatar = gravatar

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    blurb = models.TextField(default='…')

    def __unicode__(self):
        return unicode(self.user)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', (), {'username': self.user.username})

# Monkey-patch get_profile so it creates one if it doesn't exist.

orig_get_profile = User.get_profile
def get_profile(self):
    try:
        return orig_get_profile(self)
    except UserProfile.DoesNotExist:
        u = UserProfile(user=self)
        u.save()
        return u
User.get_profile = get_profile
