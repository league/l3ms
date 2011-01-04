# l3ms.accounts.tests    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib.auth import SESSION_KEY
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from l3ms.email_validation.models import ValidationKey
from l3ms.http_auth.tests import login_helper, login_redirect, setup_users

def profile_of(u):
    return reverse('profile',
                   kwargs={'username': u.username})

class AccountTest(TestCase):
    def setUp(self):
        setup_users(self)
        self.u1.is_staff = True
        self.u1.save()
        self.client = Client()

    def test_logins_required(self):
        for p in [reverse('home'),
                  profile_of(self.u2)]:
            self.client.logout()
            login_redirect(self, self.u1, self.p1, p)

    def test_profiles(self):
        login_helper(self.client, self.u1, self.p1)
        r = self.client.get(reverse('home'))
        self.assertContains(r, self.u1.username)
        r = self.client.get(profile_of(self.u2))
        self.assertContains(r, self.u2.username)

    def test_profile_privileges(self):
        self.assertTrue(self.u1.is_staff) # Alice is staff
        login_helper(self.client, self.u1, self.p1)
        r = self.client.get(profile_of(self.u1)) # my own
        self.assertEquals(r.context['privileged'], True)
        r = self.client.get(profile_of(self.u2)) # someone else
        self.assertEquals(r.context['privileged'], True)

        self.assertFalse(self.u2.is_staff) # Bob is not staff
        login_helper(self.client, self.u2, self.p2)
        r = self.client.get(profile_of(self.u2)) # my own
        self.assertEquals(r.context['privileged'], True)
        r = self.client.get(profile_of(self.u1)) # someone else
        self.assertEquals(r.context['privileged'], False)

    def test_forgot_username(self):
        self.client.logout()
        r = self.client.post(reverse('forgot_username'))
        self.assertContains(r, 'field is required')
        r = self.client.post(reverse('forgot_username'),
                             {'email': 'chuck@example.com'})
        self.assertContains(r, 'address does not')
        r = self.client.post(reverse('forgot_username'),
                             {'email': self.u1.email}, follow=True)
        self.assertContains(r, 'has been sent')

    def test_forgot_password(self):
        self.client.logout()
        r = self.client.post(reverse('forgot_password'),
                             {'username': self.u1.username}, follow=True)
        self.assertEquals(r.status_code, 200)
        self.assertContains(r, 'has been sent')
        k = ValidationKey.objects.get(user=self.u1)
        old_pw = self.p1
        self.p1 = 'aseouh'
        r = self.client.post(k.get_absolute_url(),
                             {'new_password1': self.p1,
                              'new_password2': self.p2}, follow=True)
        self.assertContains(r, 'two password fields didn')
        r = self.client.post(k.get_absolute_url(),
                             {'new_password1': self.p1,
                              'new_password2': self.p1}, follow=True)
        self.assertContains(r, 'has been changed')
        self.assertEqual(0, ValidationKey.objects.filter(user=self.u1).count())
        r = login_helper(self.client, self.u1, old_pw)
        self.assertEqual(r.status_code, 401)
        r = login_helper(self.client, self.u1, self.p1)
        self.assertEqual(self.client.session[SESSION_KEY], self.u1.id)

    def test_edit_email_normal_user(self):
        self.assertFalse(self.u2.is_staff)
        self.client.login(username=self.u2.username,
                          password=self.p2)
        old_email = self.u2.email
        new_email = 'bob123@example.com'
        r = self.client.post(reverse('edit_email',
                                     kwargs={'username': self.u2.username}),
                             {'email': new_email}, follow=True)
        self.assertContains(r, 'has been sent')
        self.assertEquals(self.u2.email, old_email) # not changed yet

    def test_edit_email_staff_user(self):
        self.assertTrue(self.u1.is_staff)
        self.client.login(username=self.u1.username, password=self.p1)
        old_email = self.u2.email
        new_email = 'bob456@example.com'
        r = self.client.post(reverse('edit_email',
                                     kwargs={'username': self.u2.username}),
                             {'email': new_email}, follow=True)
        self.assertEquals(self.u2.email, new_email)
        self.assertContains(r, 'has been changed')
