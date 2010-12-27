from django.conf.urls.defaults import *
from django.contrib import admin
from djlms.settings import rel_url
import django.contrib.auth.views
import djlms.misc.views

admin.autodiscover()

urlpatterns = patterns(
    '',
    (rel_url('misc/$'), djlms.misc.views.hello),
    (rel_url('accounts/login/$'), django.contrib.auth.views.login),
    (rel_url(r'admin/'), include(admin.site.urls)),
)
