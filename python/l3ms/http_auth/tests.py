# l3ms.http_auth.tests    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from views import SESSION_LOGOUT
import base64

class AuthTest(TestCase):
    def setUp(self):
        self.u1 = User(username='alice', email='alice@example.com')
        self.u1.set_password('alice')
        self.u1.save()
        self.u2 = User(username='bob', email='bob@example.com')
        self.u2.set_password('bob')
        self.u2.save()
        self.c = Client()

    def test_auth_required(self):
        r = self.c.get(reverse('auth_login'))
        self.assertEqual(r.status_code, 401)

    def login_helper(self, u, pw):
        a = base64.b64encode('%s:%s' % (u.username, pw))
        return self.c.get(reverse('auth_login'), {}, True,
                          HTTP_AUTHORIZATION='Basic %s' % a)

    def test_login_okay(self):
        r = self.login_helper(self.u1, 'alice')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.c.session['_auth_user_id'], self.u1.id)

    def test_logout(self):
        r = self.login_helper(self.u2, 'bob')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.c.session['_auth_user_id'], self.u2.id)
        r = self.c.get(reverse('auth_logout'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue('_auth_user_id' not in self.c.session)
        self.assertTrue(SESSION_LOGOUT in self.c.session)
        r = self.login_helper(self.u2, 'bob')
        self.assertEqual(r.status_code, 401) # first login should fail
        r = self.login_helper(self.u2, 'bob')
        self.assertEqual(r.status_code, 200) # but can login again after

    def test_login_rejected(self):
        r = self.login_helper(self.u1, 'foo')
        self.assertEqual(r.status_code, 401)

    def test_login_required(self):
        r = self.c.get(reverse('auth_test'))
        self.assertRedirects(r, reverse('auth_options'))
        r = self.login_helper(self.u2, 'bob')
        self.assertRedirects(r, reverse('auth_test')) # tests next redirect
