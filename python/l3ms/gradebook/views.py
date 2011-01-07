from django.db import transaction
from django.http import HttpResponse
from l3ms.courses.models import Course, Enrollment
from l3ms.http_auth.views import check_login
from models import *
import json
import traceback

def r(code, mesg):
    return HttpResponse(mesg, status=code, content_type='text/plain')

@transaction.commit_on_success
def post_grades(request, tag):
    if request.method != 'POST':
        return r(501, 'NOT IMPLEMENTED: we only support POST')
    try:
        course = Course.objects.get(pk=tag)
    except Course.DoesNotExist:
        return r(404, 'NOT FOUND: %s does not exist' % tag)
    # It will be much easier to post grades from scripts if it can use
    # HTTP Authentication, and not require a Django session.
    if request.user.is_authenticated():
        user = request.user
    else:
        user = check_login(request)
        if not user:
            return r(401, 'HTTP_AUTHORIZATION required\n')
    # To post grades, user must be an instructor of the given course.
    if not Enrollment.objects.filter(course=course, user=user, kind='I'):
        return r(403, 'FORBIDDEN: %s is not an instructor of %s' %
                 (user.username, course.tag))

    # Okay, NOW we're ready to go.
    try:
        data = json.loads(request.raw_post_data)
        log = []
        for d in data:
            # need to catch exceptions
            Category.objects.sync(course, d, log)
        return r(200, '%s\n' % ('\n'.join(log) if log else 'no changes'))
    except:
        return r(400, '%s\nTRANSACTION NOT COMMITTED\n' %
                 traceback.format_exc())
