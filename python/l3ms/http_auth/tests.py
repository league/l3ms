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

def login_helper(c, u, pw):
    a = base64.b64encode('%s:%s' % (u.username, pw))
    return c.get(reverse('auth_login'), {}, True,
                 HTTP_AUTHORIZATION='Basic %s' % a)

def login_redirect(test, u, pw, path):
    test.assertTrue(SESSION_KEY not in test.client.session)
    r = test.client.get(path)
    test.assertRedirects(r, reverse('auth_options'))
    r = login_helper(test.client, u, pw)
    test.assertRedirects(r, path)
    test.assertEqual(test.client.session[SESSION_KEY], u.id)

def create_test_user(username, password, email='',
                     first_name='', last_name=''):
    u = User(username=username, email=email,
             first_name=first_name, last_name=last_name)
    u.set_password(password)
    u.save()
    return u

def setup_users(test):
    test.p1 = random().hex()
    test.u1 = create_test_user('alice', test.p1, 'alice@example.com',
                               'Alice', 'Andersen')
    test.p2 = random().hex()
    test.u2 = create_test_user('bob', test.p2, 'bob@example.com')
User(username='alice', email='alice@example.com')

class AuthTest(TestCase):
    def setUp(self):
        setup_users(self)
        self.client = Client()

    def test_auth_required(self):
        r = self.client.get(reverse('auth_login'))
        self.assertEqual(r.status_code, 401)

    def test_login_okay(self):
        r = login_helper(self.client, self.u1, self.p1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.session[SESSION_KEY], self.u1.id)

    def test_logout(self):
        r = login_helper(self.client, self.u2, self.p2)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.session[SESSION_KEY], self.u2.id)
        r = self.client.get(reverse('auth_logout'), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(SESSION_KEY not in self.client.session)
        self.assertTrue(SESSION_LOGOUT in self.client.session)
        r = login_helper(self.client, self.u2, self.p2)
        self.assertEqual(r.status_code, 401) # first login should fail
        r = login_helper(self.client, self.u2, self.p2)
        self.assertEqual(r.status_code, 200) # but can login again after

    def test_login_rejected(self):
        r = login_helper(self.client, self.u1, 'foo')
        self.assertEqual(r.status_code, 401)

    def test_login_required(self):
        login_redirect(self, self.u2, self.p2, reverse('auth_test'))
