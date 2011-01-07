from django.contrib.auth.models import User
from django.db import models
from l3ms.courses.models import Course

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
        category = sync_logic(['slice_start', 'slice_stop', 'aggregate'],
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
    slice_start = models.IntegerField(null=True, blank=True)
    slice_stop = models.IntegerField(null=True, blank=True)
    aggregate = models.CharField(max_length=32)
    order = models.FloatField(default=0.0, blank=True)

    objects = CategoryManager()

    def __unicode__(self):
        """Sample: cs150s11 Quizzes"""
        return '%s %s' % (self.course.tag, self.name)

    def dump(self):
        return {'category': self.name,
                'slice_start': self.slice_start,
                'slice_stop': self.slice_stop,
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

class GradedItem(models.Model):
    category = models.ForeignKey(GradeCategory)
    name = models.CharField(max_length=72)
    points = models.IntegerField()
    feedback = models.TextField(blank=True)
    posted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now_add=True)

    objects = GradedItemManager()

    def __unicode__(self):
        """Sample: cs150s11 Quiz 1"""
        return '%s %s' % (self.category.course.tag, self.name)

    def dump(self):
        return {'item': self.name,
                'points': self.points,
                'feedback': self.feedback,
                'scores': Score.objects.dump(self)}

    class Meta:
        unique_together = ('category', 'name')
        ordering = ['-posted']  # reverse chron

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

    def dump(self):
        return {'user': self.user.username,
                'points': self.points,
                'feedback': self.feedback}

    class Meta:
        unique_together = ('item', 'user')

