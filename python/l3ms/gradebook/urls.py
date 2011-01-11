from django.conf.urls.defaults import *
from l3ms.courses import views as courses
import views

urlpatterns = patterns(
    '',
    url(r'^(?P<tag>\w+)/post$', views.post_grades, name='post_grades'),
    url(r'^(?P<tag>\w+)/dump$', views.dump_grades, name='dump_grades'),
    url(r'^(?P<tag>\w+)/details/(?P<id>\d+)', views.grade_details,
        name='grade_details'),
    )

courses.ONE_COURSE_VIEWS.append(views.grade_summary)
