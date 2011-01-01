from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^$', views.options, name='auth_options'),
    url(r'^login\b(?P<next>.*)$', views.login, name='auth_login'),
    url(r'^logout$', views.logout, name='auth_logout'),
    )
