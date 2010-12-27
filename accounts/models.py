from django.db import models
from django.contrib.auth.models import User
from base64 import urlsafe_b64encode
from hashlib import md5
from random import random

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    valid_email = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def complete(self):
        return bool(self.user.username and self.user.first_name and
                    self.user.last_name and self.user.email and
                    self.user.has_usable_password())

class ActivationManager(models.Manager):
    def create(self, user, action, email):
        r = email + random().hex()
        k = urlsafe_b64encode(md5(r).digest()[1:])
        ak = self.model(key=k, action=action, user=user, email=email)
        # send email here too?
        ak.save()

class ActivationKey(models.Model):
    key = models.CharField(max_length=20, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=4)
    user = models.ForeignKey(User)
    email = models.EmailField()

    objects = ActivationManager()

