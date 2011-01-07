from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^(?P<tag>\w+)/$', views.post_grades, name='post_grades'),
    )

