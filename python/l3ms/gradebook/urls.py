from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^(?P<tag>\w+)/post$', views.post_grades, name='post_grades'),
    url(r'^(?P<tag>\w+)/dump$', views.dump_grades, name='dump_grades'),
    )

