# l3ms.accounts.tests    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from l3ms.accounts.views import reverse_u, profile_of
from l3ms.email_validation.models import ValidationKey
from l3ms.http_auth.tests import login_helper, login_redirect, setup_users

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
        self.assertTrue(r.context['privileged'])
        r = self.client.get(profile_of(self.u2)) # someone else
        self.assertTrue(r.context['privileged'])

        self.assertFalse(self.u2.is_staff) # Bob is not staff
        login_helper(self.client, self.u2, self.p2)
        r = self.client.get(profile_of(self.u2)) # my own
        self.assertTrue(r.context['privileged'])
        r = self.client.get(profile_of(self.u1)) # someone else
        self.assertFalse(r.context['privileged'])

    def test_forgot_username(self):
        self.client.logout()
        r = self.client.post(reverse('forgot_username'))
        self.assertContains(r, 'field is required')
        r = self.client.post(reverse('forgot_username'),
                             {'email': 'chuck@example.com'})
        self.assertContains(r, 'address does not')
        r = self.client.post(reverse('forgot_username'),
                             {'email': self.u1.email}, follow=True)
        self.assertContains(r, self.u1.username)

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

    def edit_email(self, user, new_email):
        return self.client.post(reverse_u('edit_email', user.username),
                                {'email': new_email}, follow=True)

    def test_edit_email_normal_user(self):
        self.assertFalse(self.u2.is_staff)
        self.client.login(username=self.u2.username,
                          password=self.p2)
        old_email = self.u2.email
        new_email = 'bob123@example.com'
        r = self.edit_email(self.u2, new_email)
        self.assertContains(r, 'has been sent')
        self.assertEquals(self.u2.email, old_email) # not changed yet

    def test_edit_email_staff_user(self):
        self.assertTrue(self.u1.is_staff)
        self.client.login(username=self.u1.username, password=self.p1)
        old_email = self.u2.email
        new_email = 'bob456@example.com'
        r = self.edit_email(self.u2, new_email)
        self.assertContains(r, 'has been changed')
        self.u2 = User.objects.get(id=self.u2.id) # reload
        self.assertEquals(self.u2.email, new_email)

    def test_edit_email_forbidden(self):
        self.client.logout()
        new_email = 'bob789@example.com'
        r = self.edit_email(self.u1, new_email)
        self.assertEquals(r.status_code, 403) # forbidden, not logged in
        self.assertFalse(self.u2.is_staff)
        self.client.login(username=self.u2.username, password=self.p2)
        r = self.edit_email(self.u1, new_email)
        self.assertEquals(r.status_code, 403) # forbidden, not staff

    def edit_password(self, username, oldp, newp1, newp2):
        return self.client.post(reverse_u('edit_password', username),
                                {'old_password': oldp,
                                 'new_password1': newp1,
                                 'new_password2': newp2}, follow=True)

    def test_edit_password(self):
        old_pw = self.p1
        self.client.login(username=self.u1.username, password=old_pw)
        self.p1 = '09872094'
        r = self.edit_password(self.u1.username, old_pw, self.p1, self.p2)
        self.assertContains(r, 'two password fields didn')
        self.client.logout()

        self.client.login(username=self.u1.username, password=old_pw)
        r = self.edit_password(self.u1.username, self.p1, self.p1, self.p1)
        self.assertContains(r, 'entered incorrectly')
        self.client.logout()

        self.client.login(username=self.u1.username, password=old_pw)
        r = self.edit_password(self.u1.username, old_pw, self.p1, self.p1)
        self.assertEquals(r.status_code, 200)
        self.client.logout()

        self.client.login(username=self.u1.username, password=self.p1)

    def register(self, username='chuck', email='chuck@example.com',
                 first='Chuck', last='Chan', p1='chu2k', p2='chu2k'):
        return self.client.post(reverse('register'),
                                {'first_name': first, 'last_name': last,
                                 'username': username, 'email': email,
                                 'password1': p1, 'password2': p2},
                                follow=True)

    def test_registration(self):
        self.client.logout()
        r = self.register()
        self.assertContains(r, 'awaiting activation')
        u = User.objects.get(username='chuck')
        k = ValidationKey.objects.get(user=u)
        r = self.client.get(k.get_absolute_url(), follow=True)
        self.assertContains(r, 'is activated')
        r = login_helper(self.client, u, 'chu2k')
        self.assertEqual(self.client.session[SESSION_KEY], u.id)
        self.assertContains(r, 'Chuck Chan')

    def test_registration_errors(self):
        self.client.logout()
        r = self.register(username='chuck2') # should work
        self.assertContains(r, 'awaiting activation')
        r = self.register(username='chuck2') # fail, same username
        self.assertContains(r, 'already exists')
        r = self.register(username='chuck3') # fail, same email
        self.assertContains(r, 'already exists')
        r = self.register(username='chuck3', email='')
        self.assertContains(r, 'is required')
        r = self.register(username='chuck3', last='')
        self.assertContains(r, 'is required')
        r = self.register(username='chuck3', email='chuck3')
        self.assertContains(r, 'Enter a valid')
