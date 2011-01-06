from django.http import HttpResponse

def all_courses(request):
    return HttpResponse('not implemented')

def one_course(request, tag):
    return HttpResponse('%s not implemented' % tag)
