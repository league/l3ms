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
    rel_url('login', 'accounts/login/$', accounts.login),
    rel_url('logout', 'accounts/logout/$', accounts.logout),
    rel_url('register', 'accounts/new/$', accounts.register),
    rel_url('forgot_username', 'forgot/username/$', accounts.forgot_username),
    rel_url('forgot_password', 'forgot/password/$', accounts.forgot_password),
    rel_url('edit_email', 'edit/email/$', accounts.edit_email),
    rel_url('edit_profile', 'edit/profile/$', accounts.edit_profile),
    rel_url('profile', 'user/(?P<username>\w+)/$', accounts.profile),
    rel_url('navbar', 'nav/$', accounts.navbar),

#    rel_url('students', 'students/(?P<course_id>\w+)/$',
#            'djlms.courses.views.students'),
#    rel_url('scores', 'scores/(?P<course_id>\w+)/$',
#            'djlms.scores.views.scores'),

    (rel(r'admin/'), include(admin.site.urls)),
)
