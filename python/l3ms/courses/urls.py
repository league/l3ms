from django.conf import settings
from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^$', views.all_courses, name='all_courses'),
    url(r'^(?P<tag>\w+)/$', views.one_course, name='one_course'),
    )

