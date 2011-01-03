from django.conf import settings
from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^forgot/username$', views.forgot_username, name='forgot_username'),
    url(r'^forgot/password$', views.forgot_password, name='forgot_password'),
    )

