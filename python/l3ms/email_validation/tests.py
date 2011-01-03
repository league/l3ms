# l3ms.email_validation.tests    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import Client
from models import ValidationKey, UnknownValidator
from random import random

def nop_handler(request, k):
    s = str(k)
    k.delete()
    return HttpResponse(s)

ValidationKey.objects.register(
    '!', 'immediate_expire', 'email/test.txt', nop_handler, -1
    )

ValidationKey.objects.register(
    '@', 'normal', 'email/test.txt', nop_handler, 10
    )

def build_uri(self, path='/'):
    return 'http://example.com%s' % path

class ValidationTest(TestCase):

    def setUp(self):
        self.u1 = User(username='alice', email='alice@example.com')
        self.u1.save()
        self.u2 = User(username='bob', email='bob@example.com')
        self.u2.save()
        self.vo = ValidationKey.objects
        self.k1 = self.vo.create(build_uri, self.u1.email, self.u2, '@')
        self.k2 = self.vo.create(build_uri, self.u2.email, self.u2, '@')

    def test_unknown(self):
        self.assertRaises(UnknownValidator,
                          self.vo.create,
                          build_uri, self.u1.email, self.u2, '#')


    def test_create(self):
        self.assertEqual(self.k1.email, self.u1.email)
        self.assertEqual(self.k1.user.username, self.u2.username)
        self.assertEqual(self.k1.action, '@')

    def test_render(self):
        url = random().hex()
        s = self.vo.validators['@'].render(self.k1, url)
        d = eval(s)
        self.assertEqual(d['user'], self.u2.username)
        self.assertEqual(d['email'], self.u1.email)
        self.assertEqual(d['site_name'], settings.SITE_NAME)
        self.assertEqual(d['url'], url)

    def test_expiry(self):
        for i in range(20):
            for a in ['@', '!']:
                self.vo.create(build_uri, 'test%d@example.com' % i,
                               self.u2, a)
        n = self.vo.count()
        self.vo.delete_expired()
        m = self.vo.count()
        self.assertEqual(n-20, m)
        for k in self.vo.all():
            self.assertEqual(k.action, '@')

    def test_click(self):
        self.assertTrue(self.vo.count() > 0)
        c = Client()
        for k in self.vo.all():
            r = c.get(k.get_absolute_url())
            self.assertEqual(r.status_code, 200)
            r = c.get(k.get_absolute_url())
            self.assertEqual(r.status_code, 404)
        self.assertEqual(0, self.vo.count())
