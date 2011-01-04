# l3ms.email_validation.models    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

"""Data model for click-back validation links."""

from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template import loader, Context
from hashlib import md5
from random import random
from settings import FROM_EMAIL, SITE_NAME

class UnknownValidator(StandardError):
    pass

class Validator:
    """A tuple of values needed to implement a validator.

    `code` is a one-letter key to distinguish this validator.

    `subject` will be used as the subject line of the email message.

    `template` is the name of template for body of the email message.

    `handler` is a function of (request, key_object) to handle the
    click-back.

    `expiry_hours` indicates how long to keep this key in the
    database.
    """
    def __init__(self, code, subject, template, handler, expiry_hours):
        self.code = code
        self.subject = subject
        self.template = template
        self.handler = handler
        self.expiry = timedelta(hours=expiry_hours)

    def render(self, obj, url):
        """Produce the body of the email message from a template.

        The template receives the following variables:

        `user` is the instance of User to whom we're sending this
        message.

        `email` is the address to which we're sending this message.
        It may not be the same as `user.email` if we're validating a
        new address for that user.

        `site_name` is taken from `settings.SITE_NAME` to indicate the
        name of the site sending this message.

        `url` is the full URL that will trigger validation when
        clicked.
        """
        t = loader.get_template(self.template)
        c = Context({'user': obj.user,
                     'email': obj.email,
                     'site_name': SITE_NAME,
                     'url': url})
        return t.render(c)

class ValidationManager(models.Manager):
    """Additional methods for ValidationKey.objects."""

    def __init__(self, *args, **kwargs):
        self.validators = {}
        super(ValidationManager, self).__init__(*args, **kwargs)

    def register(self, code, subject, template, handler, expiry_hours):
        """Register a new validator identified by char in CODE."""
        assert code not in self.validators
        self.validators[code] = Validator(code, subject, template,
                                          handler, expiry_hours)

    def dispatch(self, request, obj):
        """Invoke the handler for validation key OBJ."""
        return self.validators[obj.action].handler(request, obj)

    def create(self, build_uri, email, user, code):
        """Generate a validation key, save, and send it by email.

        `build_uri` is a function to generate a full link (including
        http and hostname) given an absolute path.  It can be provided
        with request.build_absolute_uri in a view method.

        `email` is the address to which to send the validation link.
        It may or may not be the same as USER.email.

        `user` is the User instance to whom we are sending this link.
        The EMAIL was provided separately in case we are validating a
        new address for this user.

        `code` is the single-letter code to distinguish the type of
        validation.

        Testing some assumptions about generating keys:

        First 4 chars of float hex representation always '0x1.'
        >>> random().hex()[:4]
        '0x1.'

        Need to slice a byte off of MD5 digest to make it encode with
        an integer number of Base64 characters.
        >>> len(md5('').digest()[1:])*8%6
        0
        """

        # Combine random and non-random parts; slice off first 4 chars
        # of random float hex representation — they’re always '0x1.'
        r = code + email + random().hex()[4:]

        # Slice first byte off of MD5 digest so it's an integer number
        # of base-64 chars.  (
        key = urlsafe_b64encode(md5(r).digest()[1:])

        try:
            v = self.validators[code]
        except KeyError:
            raise UnknownValidator(code)
        obj = self.model(key=key, email=email, user=user, action=code,
                         expiry=datetime.now() + v.expiry)
        obj.save()

        url = build_uri(obj.get_absolute_url())
        send_mail(v.subject, v.render(obj, url), FROM_EMAIL, [email])
        return obj

    def delete_expired(self):
        "Delete expired keys."
        self.filter(expiry__lt = datetime.now()).delete()

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
