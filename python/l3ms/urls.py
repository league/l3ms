from django.conf.urls.defaults import *
from django.contrib import admin
from settings import URL_PREFIX, DEBUG
from accounts import views as accounts
from email_validation import views as validation
import http_auth.urls

def rel(path):
    assert not path.startswith('/')
    return '^' + URL_PREFIX + path

def rel_url(name, path, view):
    assert not path.startswith('/')
    return url(rel(path), view, name=name)

admin.autodiscover()

urlpatterns = patterns(
    '',
    rel_url('validate', 'validate/(?P<key>.*)$', validation.validate),
    rel_url('home', '$', accounts.home),
    rel_url('OLDlogin', 'u/login/$', accounts.login),
    rel_url('OLDlogout', 'u/logout/$', accounts.logout),
    rel_url('register', 'u/new/$', accounts.register),
    rel_url('activate', 'u/activate/(?P<key>.*)$', accounts.activate),
    rel_url('forgot_username', 'u/username/$', accounts.forgot_username),
    rel_url('forgot_password', 'u/password/$', accounts.forgot_password),
    rel_url('edit_email', 'u/email/$', accounts.edit_email),
    rel_url('edit_profile', 'u/profile/$', accounts.edit_profile),
    rel_url('profile', 'user/(?P<username>\w+)/$', accounts.profile),
    rel_url('navbar', 'nav/(?P<path>.*)$', accounts.navbar),

#    rel_url('students', 'students/(?P<course_id>\w+)/$',
#            'l3ms.courses.views.students'),
#    rel_url('scores', 'scores/(?P<course_id>\w+)/$',
#            'l3ms.scores.views.scores'),

    (rel(r'auth/'), include(http_auth.urls)),
    (rel(r'admin/'), include(admin.site.urls)),
)

if DEBUG:
    urlpatterns += patterns(
        '',
        rel_url('test_validation',
                'test/valid/(?P<code>\w)(?P<user>\d+)/(?P<email>.+)$',
                validation.test)
        )
