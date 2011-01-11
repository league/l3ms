# l3ms.gradebook.views    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader, Context
from l3ms.courses.models import Course, Enrollment
from l3ms.courses.templatetags.enrollment import ROSTER_GRAVATAR_SIZE
from l3ms.http_auth.views import check_login
from l3ms.http_auth.views import login_required
from l3ms.utils import except404
from models import GradedItem
import httplib
import json
import re
import traceback
import urllib

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
        GradedItem.objects.sync(data, log, course=course)
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

    return ResponseExn(200, course.gradeditem.dump()).as_json()

def grade_summary(request, context):
    c = context['course']
    u = request.user
    try:
        g = c.gradeditem
        e = u.enrollment_set.get(course=c)
    except GradedItem.DoesNotExist:
        return
    except Enrollment.DoesNotExist:
        return
    if e.is_instructor():
        context['gradeSheet'] = instructor_summary(g,e)
    else:
        context['gradeSummary'] = student_summary(g,e)

def student_summary(g, e):
    t = loader.get_template('gradebook/summary-line.html')
    buf = ['<table id="gradeSummary">']

    def recur(item, depth=0):
        item['depth'] = depth
        item['course'] = e.course
        if 'aggregate' in item:
            for i in item['items']:
                recur(i, depth+1)
            item['class'] = 'aggregate'
            buf.append(t.render(Context(item)))
        else:
            item['class'] = 'item'
            buf.append(t.render(Context(item)))

    recur(g.summary(e.user))
    buf.append('</table>')
    return ''.join(buf)


def instructor_summary(g, e):
    orphan = re.compile(r'\s+(\w{1,2}\b)')
    buf = ['<table id="gradeSheet" class="sortable">']

    def recur(item, user, template, depth=0, ancestors=[]):
        if depth == 0:
            item['expanded'] = True
            classes = []
        else:
            item['expanded'] = False
            classes = ['descendantOf%d' % a for a in ancestors]
            classes.append('childOf%d' % ancestors[0])
            if depth >= 2:
                classes.append('hidden')

        item['classes'] = classes
        item['name'] = orphan.sub(r'&nbsp;\1', item['name'])
        item['course'] = e.course
        item['user'] = user

        buf.append(template.render(Context(item)))
        for i in item.get('items', []):
            recur(i, user, template, depth+1, [item['id']] + ancestors)

    # Use instructor's 'grades' to construct header row
    data = g.summary(e.user)
    buf.append('<tr><th class="sorttable_nosort">&nbsp;</th><th>Student</th>')
    recur(data, e.user, loader.get_template('gradebook/sheet-head.html'))
    buf.append('</tr>')

    row_head = loader.get_template('gradebook/row-head.html')
    sheet_cell = loader.get_template('gradebook/sheet-cell.html')
    for s in e.course.get_graded_students():
        buf.append('<tr>')
        cx = Context({'u': s.user, 'size': ROSTER_GRAVATAR_SIZE})
        buf.append(row_head.render(cx))
        recur(g.summary(s.user), s.user, sheet_cell)
        buf.append('</tr>')

    buf.append('<tfoot><tr><td>&nbsp;</td><td>&nbsp;</td>')
    recur(data, e.user, loader.get_template('gradebook/sheet-foot.html'))
    buf.append('</tr></tfoot></table>')
    return ''.join(buf)

@login_required
@except404([Course.DoesNotExist, GradedItem.DoesNotExist,
            Enrollment.DoesNotExist])
def grade_details(request, tag, id):
    course = Course.objects.get(tag=tag)
    item = GradedItem.objects.get(id=id)
    if item.get_course() != course:
        raise GradedItem.DoesNotExist()
    enroll = course.enrollment_set.get(user=request.user) # 404? 403?
    histo = {}
    my_bucket = []
    my_summary = []

    def summarize(user):
        summ = item.summary(user)
        summ['user'] = user
        bucket = int(summ['percent']-0.5)/2
        histo[bucket] = histo.get(bucket,0) + 1
        if user == request.user:
            my_bucket.append(bucket)
            my_summary.append(summ)
        return summ

    es = course.get_graded_students()
    data = [summarize(e.user) for e in es]

    chart_dim = 600,150
    chart = {}
    chart['cht'] = 'bvg'
    chart['chs'] = '%dx%d' % (chart_dim[0], chart_dim[1])
    chart['chbh'] = '10,1,1'
    chart['chco'] = ','.join(['DEBDDE' if b in my_bucket else '00A5C6'
                              for b in range(0,50)])
    chart['chxt'] = 'x,y'
    k = max(histo.values())
    chart['chxr'] = '0,0,100,4|1,0,%d,1' % k
    chart['chds'] = '0,%d' % k
    chart['chd'] = 't:'
    chart['chd'] += '|'.join([str(histo.get(b,0)) for b in range(0,50)])
#    chart['chof'] = 'validate'
    chart = urllib.urlencode(chart)

    if not enroll.is_instructor():
        data = my_summary

    # Gather score for current user, and scores for all users.
    return render_to_response('gradebook/details.html',
                              {'site_name': settings.SITE_NAME,
                               'course': course,
                               'item': item,
                               'user': request.user,
                               'chart': chart,
                               'chart_dim': chart_dim,
                               'data': data})
