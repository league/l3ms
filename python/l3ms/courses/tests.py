# l3ms.courses.tests    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from datetime import date
from django.contrib.auth.models import Group, User
from models import Semester, Course, Enrollment, CourseLink
import random

def _flip():
    return bool(random.getrandbits(1))

def create_semester(nm, y, sm, sd, em, ed):
    s = Semester(tag = '%s%02d' % (nm[0].lower(), y%100),
                 name = '%s %d' % (nm, y),
                 start_date = date(year=y, month=sm, day=sd),
                 end_date = date(year=y, month=em, day=ed))
    s.save()

def create_sample_courses():
    for y in range(2009,2012):
        create_semester('Fall', y, 9, 1, 12, 31)
        create_semester('Spring', y, 1, 1, 5, 30)
    semesters = Semester.objects.all()

    for co,nm in [("CS 101", "Fundamentals of Computer Science"),
                  ("CS 102", "Programming I"),
                  ("CS 117", "Programming II"),
                  ("CS 150", "Operating Systems"),
                  ("CS 164", "Software Engineering"),
                  ("CS 130", "Algorithms & Data Structures")]:
        for sem in random.sample(semesters, 3):
            tag = co.replace(' ', '').lower() + sem.tag
            grp = Group(name=tag)
            grp.save()
            key = '%x' % random.getrandbits(24)
            c = Course(tag=tag, name=nm, code=co, semester=sem,
                       group=grp, key=key,
                       is_active=_flip())
            c.save()

            us = random.sample(User.objects.all(), random.randrange(4,8))
            num_instructors = random.choice([1,2])
            instrs = us[:num_instructors]
            studs = us[num_instructors:]

            for u in us:
                e = Enrollment(course=c, user=u,
                               kind = 'I' if u in instrs
                               else random.choice(['A', 'G']),
                               notify_on_commit = _flip(),
                               notify_new_grades = _flip())
                e.save()

            ln = CourseLink(course=c, kind='H',
                            url='http://liucs.net/%s/' % tag)
            ln.save()

            if _flip():
                ln = CourseLink(course=c, kind='T',
                                url='http://amazon.com/%s' % nm)
                ln.save()

            if _flip():
                fmt = random.choice(['http://liucs.net/svn/%s/',
                                     'http://github.com/league/%s'])
                ln = CourseLink(course=c, kind='R', url=fmt % tag)
                ln.save()
