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
import re

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

ONE_COURSE_VIEWS=[]

@login_required
@except404([Course.DoesNotExist])
def one_course(request, tag):
    course = Course.objects.get(pk=tag)

    # Maybe ask for enrollment key instead
    if not enrolled_in(request.user, tag):
        return enroll(request, course)
    enrollment = Enrollment.objects.get(user=request.user, course=course)

    # Course page has a preferences section, handled by this POST.
    if request.method == 'POST':
        form = forms.CourseOptionsForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            request.session[SESSION_MESSAGE] = M_PREFS_SAVED
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = forms.CourseOptionsForm(instance=enrollment)

    # Not a POST or form not valid, so display page as normal.

    # Session message
    message = request.session.get(SESSION_MESSAGE, '')
    if message:
        del request.session[SESSION_MESSAGE]

    # Allow other functions in ONE_COURSE_VIEWS to augment context.
    context = {'user': request.user,
               'site_name': settings.SITE_NAME,
               'course': course,
               'enrollment': enrollment,
               'form': form,
               'action': request.get_full_path(),
               'message': message}

    for view in ONE_COURSE_VIEWS:
        view(request, context)

    return render_to_response('courses/one.html', context)

def nav(request, path):
    course = None
    message = None
    try:
        course = Course.objects.get(tag__in=re.split(r'[/.]', path))
    except Course.DoesNotExist:
        message = 'DoesNotExist'
    except Course.MultipleObjectsReturned:
        message = 'MultipleObjectsReturned'

    return render_to_response('courses/nav.html',
                              {'user': request.user,
                               'site_name': settings.SITE_NAME,
                               'message': message if settings.DEBUG else '',
                               'course': course})
