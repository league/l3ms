# l3ms.http_auth.tests    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from random import random
from views import SESSION_LOGOUT
import base64

def create_sample_users():
    """Programmatically create the sample-users fixture."""
    names = [("Alice Ann", "Archer"),
             ("Bobby", "O'Neill"),
             ("Chuck", "Chan-Jones"),
             ("Diane", "Depp Walker"),
             ("Edgar", "Ent"),
             ("Fran", "Fernando"),
             ("Grant", "Greig"),
             ("Admin", "User")]

    for f,l in names:
        n = f.split(' ')[0].lower()
        e = '%s@example.com' % n
        u = User(username=n, first_name=f, last_name=l, email=e)
        u.set_password(n)
        if n == 'admin':
            u.is_staff = True
        u.save()

class AuthTest(TestCase):
    fixtures = ['sample-users.json']

    def setUp(self):
        self.u1 = User.objects.get(username='alice')
        self.p1 = self.u1.username
        self.u2 = User.objects.get(username='grant')
        self.p2 = self.u2.username
        self.client = Client()

    def login_helper(self, c, u, pw):
        a = base64.b64encode('%s:%s' % (u.username, pw))
        return c.get(reverse('auth_login'), {}, True,
                     HTTP_AUTHORIZATION='Basic %s' % a)

    def test_auth_required(self):
        r = self.client.get(reverse('auth_login'))
        self.assertEqual(r.status_code, 401)

    def test_login_okay(self):
        r = self.login_helper(self.client, self.u1, self.p1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.session[SESSION_KEY], self.u1.id)

    def test_logout(self):
        r = self.login_helper(self.client, self.u2, self.p2)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.session[SESSION_KEY], self.u2.id)
        r = self.client.get(reverse('auth_logout'), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(SESSION_KEY not in self.client.session)
        self.assertTrue(SESSION_LOGOUT in self.client.session)
        r = self.login_helper(self.client, self.u2, self.p2)
        self.assertEqual(r.status_code, 401) # first login should fail
        r = self.login_helper(self.client, self.u2, self.p2)
        self.assertEqual(r.status_code, 200) # but can login again after

    def test_login_rejected(self):
        r = self.login_helper(self.client, self.u1, 'foo')
        self.assertEqual(r.status_code, 401)

    def test_login_required(self):
        path = reverse('auth_test')
        self.assertTrue(SESSION_KEY not in self.client.session)
        r = self.client.get(path)
        self.assertRedirects(r, reverse('auth_options'))
        r = self.login_helper(self.client, self.u2, self.p2)
        self.assertRedirects(r, path)
        self.assertEqual(self.client.session[SESSION_KEY], self.u2.id)
