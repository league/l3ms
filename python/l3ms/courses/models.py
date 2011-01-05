from django.db import models
from django.contrib.auth.models import User, Group

class Semester(models.Model):
    tag = models.SlugField()
    name = models.CharField(max_length=32, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
        return self.name

class Course(models.Model):
    tag = models.SlugField()
    name = models.CharField(max_length=72)
    code = models.CharField(max_length=14)
    semester = models.ForeignKey(Semester)
    instructor = models.ManyToManyField(User, through='Enrollment')
    group = models.OneToOneField(Group)
    key = models.CharField(max_length=32)
    is_active = models.BooleanField()

    def __unicode__(self):
        return self.tag

class Enrollment(models.Model):
    course = models.ForeignKey(Course)
    student = models.ForeignKey(User)
    is_enrolled = models.BooleanField()
    notify_on_commit = models.BooleanField()
    notify_new_grades = models.BooleanField()

    def __unicode__(self):
        return '%s in %s' % (self.student.username, self.course.tag)

    class Meta:
        unique_together = (("course", "student"),)

LINK_KINDS = (
    ('H', 'Home page'),
    ('R', 'Repository'),
    ('C', 'Calendar'),
    ('T', 'Textbook'),
    ('O', 'Other'),
    )

class CourseLink(models.Model):
    course = models.ForeignKey(Course)
    kind = models.CharField(max_length=1, choices=LINK_KINDS)
    url = models.URLField(verify_exists=False)

    def __unicode__(self):
        return '%s %s %s' % (self.course.tag, self.kind, self.url)
