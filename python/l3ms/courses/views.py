from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from models import Course

def all_courses(request):
    my_courses = Course.objects.filter(enrollment__user=request.user)
    return render_to_response('courses/all.html',
                              {'user': request.user,
                               'site_name': settings.SITE_NAME,
                               'courses': Course.objects.all(),
                               'my_courses': my_courses})

def one_course(request, tag):
    return HttpResponse('%s not implemented' % tag)
