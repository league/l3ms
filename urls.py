from django.conf import global_settings as default
from django.conf.urls.defaults import *
from django.contrib import admin
from djlms.settings import rel_url
import django.contrib.auth.views
import djlms.accounts.views
import djlms.misc.views

admin.autodiscover()

urlpatterns = patterns(
    '',
    (rel_url('misc/$'), djlms.misc.views.hello),
    (rel_url(default.LOGIN_URL[1:]), django.contrib.auth.views.login,
     {'template_name': 'admin/login.html'}),
    (rel_url(default.LOGOUT_URL[1:]), django.contrib.auth.views.logout),
    (rel_url(default.LOGIN_REDIRECT_URL[1:]), djlms.accounts.views.profile),
    (rel_url(r'admin/'), include(admin.site.urls)),
)
