from django.conf import settings
from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^forgot/username$', views.forgot_username, name='forgot_username'),
    url(r'^forgot/password$', views.forgot_password, name='forgot_password'),
    url(r'^edit/(?P<username>\w+)/email$', views.edit_email, name='edit_email'),
    url(r'^edit/(?P<username>\w+)/password$', views.edit_password,
        name='edit_password'),
    url(r'^edit/(?P<username>\w+)/profile$', views.edit_profile,
        name='edit_profile'),
    url(r'^new$', views.register, name='register'),
    url(r'^all$', views.all_users, name='all_users'),
    url(r'^check/username$', views.check_username, name='check_username'),
    url(r'^check/email$', views.check_email, name='check_email'),
    )

