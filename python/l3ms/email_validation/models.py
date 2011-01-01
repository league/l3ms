# -*- coding: utf-8 -*-
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template import loader, Context
from hashlib import md5
from random import random
from settings import FROM_EMAIL

class Validator:
    def __init__(self, code, subject, template, handler, expiry_hours):
        self.code = code
        self.subject = subject
        self.template = template
        self.handler = handler
        self.expiry = timedelta(hours=expiry_hours)

class ValidationManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.validators = {}
        super(ValidationManager, self).__init__(*args, **kwargs)

    def register(self, code, subject, template, handler, expiry_hours):
        assert code not in self.validators
        self.validators[code] = Validator(code, subject, template,
                                          handler, expiry_hours)

    def dispatch(self, request, obj):
        return self.validators[obj.action].handler(request, obj)

    def create(self, request, email, user, code):
        # Combine random and non-random bits; slice off 1st 4 chars of
        # random float hex representation — they’re always '0x1.'
        r = code + email + random().hex()[4:]

        # Slice 1st byte off of MD5 digest so it's an integer number
        # of base-64 chars.
        key = urlsafe_b64encode(md5(r).digest()[1:])

        v = self.validators[code]
        obj = self.model(key=key, email=email, user=user, action=code,
                         expiry=datetime.now() + v.expiry)
        obj.save()

        url = request.build_absolute_uri(obj.get_absolute_url())
        t = loader.get_template(v.template)
        c = Context({'email': email, 'user': user, 'url': url})
        send_mail(v.subject, t.render(c), FROM_EMAIL, [email])
        return obj

class ValidationKey(models.Model):
    key = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    user = models.ForeignKey(User)
    action = models.CharField(max_length=1)
    expiry = models.DateTimeField()

    objects = ValidationManager()

    def __unicode__(self):
        return '%s %s %s' % (self.action, self.email, self.key)

    @models.permalink
    def get_absolute_url(self):
        return ('validate', (), {'key': self.key})

admin.site.register(ValidationKey)
