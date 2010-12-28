from django.conf.urls.defaults import *
from django.contrib import admin
from djlms.settings import URL_PREFIX
from djlms.accounts import views as accounts

def rel(path):
    assert not path.startswith('/')
    return '^' + URL_PREFIX + path

def rel_url(name, path, view):
    assert not path.startswith('/')
    return url(rel(path), view, name=name)

admin.autodiscover()

urlpatterns = patterns(
    '',
    rel_url('home', '$', accounts.home),
    rel_url('login', 'u/login/$', accounts.login),
    rel_url('logout', 'u/logout/$', accounts.logout),
    rel_url('register', 'u/new/$', accounts.register),
    rel_url('activate', 'u/activate/(?P<key>.*)$', accounts.activate),
    rel_url('forgot_username', 'u/username/$', accounts.forgot_username),
    rel_url('forgot_password', 'u/password/$', accounts.forgot_password),
    rel_url('edit_email', 'u/email/$', accounts.edit_email),
    rel_url('edit_profile', 'u/profile/$', accounts.edit_profile),
    rel_url('profile', 'user/(?P<username>\w+)/$', accounts.profile),
    rel_url('navbar', 'nav/(?P<path>.*)$', accounts.navbar),

#    rel_url('students', 'students/(?P<course_id>\w+)/$',
#            'djlms.courses.views.students'),
#    rel_url('scores', 'scores/(?P<course_id>\w+)/$',
#            'djlms.scores.views.scores'),

    (rel(r'admin/'), include(admin.site.urls)),
)
