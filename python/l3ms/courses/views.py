from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from l3ms.http_auth.views import login_required, SESSION_MESSAGE
from l3ms.utils import except404
from models import Course, Enrollment
from strings import *
from templatetags.enrollment import enrolled_in
import forms

def all_courses(request):
    my_courses = Course.objects.filter(enrollment__user=request.user)
    return render_to_response('courses/all.html',
                              {'user': request.user,
                               'site_name': settings.SITE_NAME,
                               'courses': Course.objects.all(),
                               'my_courses': my_courses})

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

@login_required
@except404([Course.DoesNotExist])
def one_course(request, tag):
    course = Course.objects.get(pk=tag)
    if not enrolled_in(request.user, tag):
        return enroll(request, course)
    enrollment = Enrollment.objects.get(user=request.user, course=course)
    if request.method == 'POST':
        form = forms.CourseOptionsForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            request.session[SESSION_MESSAGE] = M_PREFS_SAVED
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = forms.CourseOptionsForm(instance=enrollment)
    message = request.session.get(SESSION_MESSAGE, '')
    if message:
        del request.session[SESSION_MESSAGE]
    return render_to_response('courses/one.html',
                              {'user': request.user,
                               'site_name': settings.SITE_NAME,
                               'course': course,
                               'enrollment': enrollment,
                               'form': form,
                               'action': request.get_full_path(),
                               'message': message})
