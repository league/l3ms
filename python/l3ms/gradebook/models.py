# l3ms.gradebook.models    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib.auth.models import User
from django.db import models
from l3ms.courses.models import Course
import aggregators
import preprocessors

def symbols_in(module):
    """Return list of name/string pairs for symbols in `module`.

    This is used to construct a `choices` string for fields that
    reference functions in particular modules, like the aggregators
    for grade categories.

    >>> ('sum', 'sum') in symbols_in(aggregators)
    True
    """
    return map(lambda sym: (sym, sym),
               filter(lambda sym: not sym.startswith('_'),
                      dir(module)))

class GradedItem(models.Model):
    """Represents either one graded item, or a category.

    The connection to ‘Course’ is one-to-one, which makes it
    convenient because we can do a_course.gradeditem to get the
    top-level.  But this means that all descendants must have course =
    null — instead they'll have the parent field to another
    GradedItem."""
    course = models.OneToOneField(Course, null=True)
    parent = models.ForeignKey('GradedItem', null=True,
                               related_name='children')
    name = models.CharField(max_length=72)
    posted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now_add=True)
    order = models.FloatField(default=0.0, blank=True)
    is_composite = models.BooleanField(default=False)

    # If it is composite, we use these fields:
    preprocess = models.CharField(choices=symbols_in(preprocessors),
                                  max_length=32, blank=True)
    aggregate = models.CharField(choices=symbols_in(aggregators),
                                 max_length=32, blank=True)

    # If not composite, use these fields
    points = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    def save(self, force_insert=False, force_update=False):
        """Overridden to enforce composite constraints."""
        assert bool(self.course) ^ bool(self.parent)
        if self.is_composite:
            assert self.aggregate    # preprocess still optional
            assert not (self.points or self.feedback)
        else:
            assert self.points       # feedback still optional
            assert not (self.preprocess or self.aggregate)
        super(GradedItem, self).save(force_insert, force_update)
        # Unfortunately, must verify this AFTER save, because
        # having pk=null wreaks havoc with finding children.
        if not self.is_composite:
            assert self.children.count() == 0

    def get_course(self):
        """Return course to which this item is attached.

        This method compensates for the fact that `self.course` is
        null for all descendants of the root by climbing up the
        hierarchy."""
        return self.course or self.parent.get_course()

    def __unicode__(self):
        if self.parent:
            return u'%s → %s' % (unicode(self.parent), self.name)
        else:
            return u'%s: %s' % (self.course.tag, self.name)

    def dump(self):
        """Return a representation using lists and dictionaries."""
        if self.is_composite:
            return {'name': self.name,
                    'preprocess': self.preprocess,
                    'aggregate': self.aggregate,
                    'items': [i.dump() for i in self.children.all()]}
        else:
            return {'name': self.name,
                    'points': self.points,
                    'feedback': self.feedback}




def update_fields(entity, fields, data):
    changes = []
    for f in fields:
        if getattr(entity, f) != data[f]:
            changes.append(f)
            setattr(entity, f, data[f])
    return changes

def sync_logic(fields, manager, data, log, commit, **args):
    entity, created = manager.get_or_create(**args)
    changes = update_fields(entity, fields, data)
    if created:
        log.append('Creating %s' % entity)
    elif changes:
        log.append('Editing %s %s' % (entity, changes))
    if commit and (created or changes):
        entity.save()
    return entity

class CategoryManager(models.Manager):
    def sync(self, course, data, log, commit=True):
        category = sync_logic(['preprocess', 'aggregate'],
                              self, data, log, commit,
                              course = course,
                              name = data['category'])
        for i in data['items']:
            GradedItem.objects.sync(category, i, log, commit)

    def dump(self, course):
        return [cat.dump() for cat in self.filter(course=course)]


class GradeCategory(models.Model):
    course = models.ForeignKey(Course)
    name = models.CharField(max_length=72)
    preprocess = models.CharField(max_length=32, blank=True,
                                  choices=symbols_in(preprocessors))
    aggregate = models.CharField(max_length=32,
                                 choices=symbols_in(aggregators))
    order = models.FloatField(default=0.0, blank=True)

    objects = CategoryManager()

    def __unicode__(self):
        """Sample: cs150s11 Quizzes"""
        return '%s %s' % (self.course.tag, self.name)

    def dump(self):
        return {'category': self.name,
                'preprocess': self.preprocess,
                'aggregate': self.aggregate,
                'items': GradedItem.objects.dump(self)}

    class Meta:
        unique_together = ('course', 'name')
        ordering = ['order', 'name']
        order_with_respect_to = 'course'

class GradedItemManager(models.Manager):
    def sync(self, category, data, log, commit=True):
        item = sync_logic(['points', 'feedback'],
                          self, data, log, commit,
                          category = category,
                          name = data['item'],
                          defaults = {'points': data['points']})
        for s in data['scores']:
            Score.objects.sync(item, s, log, commit)

    def dump(self, category):
        return [i.dump() for i in self.filter(category=category)]


class ScoreManager(models.Manager):
    def sync(self, item, data, log, commit=True):
        # TODO: need to catch User.DoesNotExist somewhere
        user = User.objects.get(username=data['user'])
        sync_logic(['points', 'feedback'], self, data, log, commit,
                   item = item, user = user,
                   defaults = {'points': data['points']})

    def dump(self, item):
        return [s.dump() for s in self.filter(item=item)]

class Score(models.Model):
    item = models.ForeignKey(GradedItem)
    user = models.ForeignKey(User)
    points = models.IntegerField()
    feedback = models.TextField(blank=True)
    posted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now_add=True)

    objects = ScoreManager()

    def __unicode__(self):
        """Sample: cs150s11 Quiz 1 league 40"""
        return '%s %s %s %d' % (self.item.category.course.tag,
                                self.item.name,
                                self.user.username,
                                self.points)

    def percent_string(self):
        return '%.0f%%' % self.percent()

    def percent(self):
        return self.points * 100.0 / self.item.points

    def dump(self):
        return {'user': self.user.username,
                'points': self.points,
                'feedback': self.feedback}

    class Meta:
        unique_together = ('item', 'user')

