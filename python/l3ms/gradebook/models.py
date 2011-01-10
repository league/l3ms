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

AGGREGATORS = symbols_in(aggregators)
PREPROCESSORS = symbols_in(preprocessors)

def update_fields(entity, fields, data):
    """Update `fields` of `entity` to match values in `data` dict.

    Return the list of fields that were changed."""
    changes = []
    for f in fields:
        if getattr(entity, f) != data[f]:
            changes.append(f)
            setattr(entity, f, data[f])
    return changes

def sync_logic(fields, manager, data, log, **args):
    """Get or create an entity and update its fields.

    Append actions to the string list `log` and return the entity."""
    entity, created = manager.get_or_create(**args)
    changes = update_fields(entity, fields, data)
    if created:
        log.append('Creating %s' % entity)
    elif changes:
        log.append('Editing %s %s' % (entity, changes))
    if created or changes:
        entity.save()
    return entity

class GradedItemManager(models.Manager):
    def sync(self, data, log, course=None, parent=None):
        if 'aggregate' in data: # composite
            gi = sync_logic(['preprocess', 'aggregate'],
                            self, data, log,
                            is_composite = True,
                            course = course,
                            parent = parent,
                            name = data['name'],
                            defaults = {'aggregate': data['aggregate']})
            for i in data['items']:
                self.sync(i, log, None, gi)
        else:                   # leaf
            gi = sync_logic(['points', 'feedback'],
                            self, data, log,
                            is_composite = False,
                            course = course,
                            parent = parent,
                            name = data['name'],
                            defaults = {'points': data['points']})
            for s in data['scores']:
                Score.objects.sync(gi, s, log)

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

    objects = GradedItemManager()

    class Meta:
        unique_together = ('course', 'parent', 'name')
        ordering = ['order', 'posted', 'name']

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
        return self

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
                    'feedback': self.feedback,
                    'scores': [s.dump() for s in self.score_set.all()]}

    def summary(self, student):
        """Summarize score hierarchy for given `student`.

        This will apply the aggregation and preprocessing functions.
        The expected shape of the returned data is as follows: `{name,
        score, score_string, points, all: {score, score_string,
        points}}`.  If the item is composite, include `{aggregate,
        items}`, and possibly `{preprocess}`.  Otherwise include
        `{feedback_p}`.

        `score_string` is maintained separately, so it can be set to
        'null' if `student` is missing a score for this item.  This is
        calculated as zero, but should appear as 'null'."""

        data = {'name': self.name}

        if not self.is_composite: # Easier case first
            try:                  # Maybe score won't exist
                score = self.score_set.get(user=student)
                stats = {'score': score.points,
                         'score_string': str(score.points),
                         'points': self.points}
                data['feedback_p'] = bool(self.feedback or score.feedback)
                data['all'] = stats
                data.update(stats)
            except Score.DoesNotExist:
                stats = {'score': 0,
                         'score_string': 'null',
                         'points': self.points}
                data['feedback_p'] = bool(self.feedback)
                data['all'] = stats
                data.update(stats)

        else:                   # If it IS composite
            aggregate_f = getattr(aggregators, self.aggregate)
            data['aggregate'] = self.aggregate
            data['preprocess'] = self.preprocess

            all_ch = [c.summary(student) for c in self.children.all()]
            data['items'] = all_ch

            score = aggregate_f(lambda x: x['all']['score'], all_ch)
            points = aggregate_f(lambda x: x['all']['points'], all_ch)
            stats = {'score': score,
                     'score_string': str(score),
                     'points': points}
            data['all'] = stats

            if self.preprocess:
                slice_f = getattr(preprocessors, self.preprocess)
                slice_ch = slice_f(lambda x: x['score'], all_ch)
                score = aggregate_f(lambda x: x['score'], slice_ch)
                points = aggregate_f(lambda x: x['points'], slice_ch)
                stats = {'score': score,
                         'score_string': str(score),
                         'points': points}
            data.update(stats)

        return data

class ScoreManager(models.Manager):
    def sync(self, item, data, log):
        u = User.objects.get(username=data['user'])
        sync_logic(['points', 'feedback'],
                   self, data, log,
                   item = item,
                   user = u,
                   defaults = {'points': data['points']})

class Score(models.Model):
    item = models.ForeignKey(GradedItem)
    user = models.ForeignKey(User)
    points = models.IntegerField()
    feedback = models.TextField(blank=True)
    posted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now_add=True)

    objects = ScoreManager()

    class Meta:
        unique_together = ('item', 'user')
        order_with_respect_to = 'item'
        ordering = ['user']

    def save(self, force_insert=False, force_update=False):
        """Overridden to enforce composite constraints."""
        assert not self.item.is_composite
        super(Score, self).save(force_insert, force_update)

    def __unicode__(self):
        return '%s %s %s %d' % (self.item.get_course().tag,
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
