from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from l3ms.http_auth.views import login_required
from l3ms.utils import except404
from models import Course
from templatetags.enrollment import enrolled_in
import forms

def all_courses(request):
    my_courses = Course.objects.filter(enrollment__user=request.user)
    return render_to_response('courses/all.html',
                              {'user': request.user,
                               'site_name': settings.SITE_NAME,
                               'courses': Course.objects.all(),
                               'my_courses': my_courses})

@login_required
@except404([Course.DoesNotExist])
def one_course(request, tag):
    course = Course.objects.get(pk=tag)
    if enrolled_in(request.user, tag):
        return HttpResponse('%s okay' % tag)
    else:
        return enroll(request, course)

def enroll(request, course):
    assert request.user.is_authenticated()
    assert not enrolled_in(request.user, course.tag)
    if request.method == 'POST':
        form = forms.EnrollmentForm(request.user, course, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = forms.EnrollmentForm(request.user, course)
    return render_to_response('courses/enroll.html',
                              {'user': request.user,
                               'course': course,
                               'site_name': settings.SITE_NAME,
                               'form': form,
                               'action': request.get_full_path()})
