from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^$', views.options, name='auth_options'),
    url(r'^login$', views.login, name='auth_login'),
    url(r'^logout$', views.logout, name='auth_logout'),
    url(r'^test$', views.test, name='auth_test'),
    )
