# l3ms.courses.models    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.db import models
from django.contrib.auth.models import User, Group
from urlparse import urlsplit

class Semester(models.Model):
    tag = models.SlugField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-end_date']

class Course(models.Model):
    tag = models.SlugField(primary_key=True)
    name = models.CharField(max_length=72)
    code = models.CharField(max_length=14)
    semester = models.ForeignKey(Semester)
    group = models.OneToOneField(Group)
    key = models.CharField(max_length=32)
    is_active = models.BooleanField()

    def __unicode__(self):
        return self.tag

    def get_users_by_kind(self, kind, incl=True):
        q = self.enrollment_set
        q = q.filter if incl else q.exclude
        q = q(kind=kind)
        q = q.order_by('user__username')
        return q

    def get_instructors(self):
        return self.get_users_by_kind('I')

    def get_students(self):
        return self.get_users_by_kind('I', False)

    def get_graded_students(self):
        return self.get_users_by_kind('G')

    def get_auditing_students(self):
        return self.get_users_by_kind('A')

    def get_full_instructor_names(self):
        return [e.user.get_full_name().replace(' ', '&nbsp;')
                for e in self.get_instructors()]

    class Meta:
        unique_together = ('semester', 'code')
        ordering = ['semester', 'code']

ENROLLMENT_KINDS = (
    ('I', 'Instructor'),
    ('A', 'Audit'),
    ('G', 'Graded'),
    )

class Enrollment(models.Model):
    course = models.ForeignKey(Course)
    user = models.ForeignKey(User)
    kind = models.CharField(max_length=1, choices=ENROLLMENT_KINDS)
    notify_on_commit = models.BooleanField(default=True)
    notify_new_grades = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s in %s' % (self.user.username, self.course.tag)

    class Meta:
        unique_together = (("course", "user"),)
        ordering = ['course']

    def is_instructor(self):
        return self.kind == 'I'

    def is_student(self):
        return self.kind != 'I'

    def is_graded(self):
        return self.kind == 'G'

    def is_auditing(self):
        return self.kind == 'A'

LINK_KINDS = (
    ('H', 'Home'),
    ('R', 'Repository'),
    ('C', 'Calendar'),
    ('T', 'Text'),
    ('F', 'Feed'),
    ('O', 'Other'),
    )

class CourseLink(models.Model):
    course = models.ForeignKey(Course)
    kind = models.CharField(max_length=1, choices=LINK_KINDS)
    url = models.URLField(verify_exists=False)

    def __unicode__(self):
        return '%s %s %s' % (self.course.tag, self.kind,
                             self.get_abbrev_url())

    def get_abbrev_url(self):
        scheme, host, path, q, frag = urlsplit(self.url)
        if len(path) > 20:
            path = path[:20]+u'…'
        return host+path
