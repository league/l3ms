from django.db import transaction
from django.http import HttpResponse
from l3ms.courses.models import Course, Enrollment
from l3ms.http_auth.views import check_login
from models import GradeCategory
import httplib
import json
import traceback

class ResponseExn:
    def __init__(self, code, data):
        self.code = code
        self.data = data

    def as_text(self):
        if self.code == 200:
            content = '%s\n' % self.data
        else:
            content = '%s: %s\n' % (httplib.responses[self.code], self.data)
        return HttpResponse(content,
                            status=self.code,
                            content_type='text/plain')

    def as_json(self):
        return HttpResponse(json.dumps(self.data, indent=2),
                            status=self.code,
                            content_type='text/plain')

# It will be much easier to post grades from scripts if it can use
# HTTP Authentication, and not require a Django session.
def validate_access(request, tag):
    try:
        course = Course.objects.get(pk=tag)
    except Course.DoesNotExist:
        raise ResponseExn(404, 'Course %s does not exist.' % tag)

    if request.user.is_authenticated():
        user = request.user
    else:
        user = check_login(request)
        if not user:
            raise ResponseExn(401, 'You did not send HTTP_AUTHORIZATION.')

    if not Enrollment.objects.filter(course=course, user=user, kind='I'):
        raise ResponseExn(403,
                          'User %s is not an instructor of %s' %
                          (user.username, tag))

    return (course, user)

@transaction.commit_on_success
def post_grades(request, tag):
    if request.method != 'POST':
        return ResponseExn(501, 'This operation supports POST only').as_text()
    try:
        course, user = validate_access(request, tag)
    except ResponseExn as r:
        return r.as_text()

    try:
        data = json.loads(request.raw_post_data)
        log = []
        for d in data:
            GradeCategory.objects.sync(course, d, log)
        return ResponseExn(200, '\n'.join(log) if log
                           else 'no changes').as_text()
    except Exception:
        return ResponseExn(400, '%s\nNOTHING COMMITTED\n' %
                           traceback.format_exc()).as_text()

def dump_grades(request, tag):
    try:
        course, user = validate_access(request, tag)
    except ResponseExn as r:
        return r.as_json()

    return ResponseExn(200, GradeCategory.objects.dump(course)).as_json()

def grade_summary(request, context):
    context['summary'] = 'I was here.'
