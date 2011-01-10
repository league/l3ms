from django.test import TestCase
from l3ms.courses.models import Course
from models import GradedItem, Score, AGGREGATORS, PREPROCESSORS
import random

def sample_feedback():
    return random.choice(['',
                          'You did well.',
                          'Here are some tips.',
                          'Must try harder.'])

def sample_preprocessor():
    return random.choice(PREPROCESSORS)[0] if random.randrange(2)==0 else ''

def sample_aggregator():
    return random.choice(AGGREGATORS)[0]

def sample_graded_item(parent, name, points):
    g = GradedItem(parent=parent, name=name, is_composite=False,
                   points=points, feedback=sample_feedback()).save()
    for e in g.get_course().enrollment_set.exclude(kind='I'):
        s = Score(item=g, user=e.user, points=random.randrange(0,points+1),
                  feedback=sample_feedback()).save() #?
    return g

def sample_grade_category(parent, name, preprocess=None, course=None):
    return GradedItem(course=course, parent=parent, name=name,
                      is_composite=True, aggregate=sample_aggregator(),
                      preprocess=preprocess if preprocess else
                      sample_preprocessor()).save()

def sample_basic_grading(course):
    tot = sample_grade_category(None, 'Basic', course=course)
    for n in ['Midterm', 'Final', 'Project']:
        sample_graded_item(tot, n, 100)

def sample_standard_grading(course):
    tot = sample_grade_category(None, 'Total', course=course)
    for c in ['Quiz', 'Exam', 'Assignment']:
        i = sample_grade_category(tot, 'Quizzes' if c=='Quiz' else c+'s')
        for k in range(1, random.randrange(4,7)):
            sample_graded_item(i, '%s %d' % (c,k),
                               random.choice([30,40,50,100]))
    sample_graded_item(tot, 'Participation', 30)

def sample_item_name(base):
    return '%s %03X' % (base, random.getrandbits(12))

def sample_graded_node(parent, max_depth):
    if random.randrange(0, max_depth) == 0:
        sample_graded_item(parent, sample_item_name('Item'),
                           random.choice([30,50,80]))
    else:
        g = sample_grade_category(parent, sample_item_name('Category'))
        for i in range(1, random.randrange(3,7)):
            sample_graded_node(g, max_depth-1)

def sample_elaborate_grading(course):
    tot = sample_grade_category(None, 'Complex', course=course)
    sample_graded_node(tot, 3)

def sample_grading():
    cs = Course.objects.all()
    for c in cs[:5]:
        sample_basic_grading(c)
    for c in cs[5:10]:
        sample_standard_grading(c)
    for c in cs[10:15]:
        sample_elaborate_grading(c)

class GradingTest(TestCase):
    fixtures = ['sample-users.json', 'sample-courses.json',
                'sample-grades.json']

    def test_dump_leaf(self):
        # Find a leaf item
        g = GradedItem.objects.filter(is_composite=False)[:1][0]
        # It should have some scores recorded
        users = [s.user.username for s in g.score_set.all()]
        self.assertTrue(len(users)>0)
        data = g.dump()
        self.assertTrue('aggregate' not in data)
        self.assertEquals(data['points'], g.points)
        self.assertEquals(len(data['scores']), len(users))
        for s in data['scores']:
            self.assertTrue(s['user'] in users)

    def test_dump_sync(self):
        """Exercise the dump() and sync() methods."""
        for g in GradedItem.objects.filter(parent=None)[:5]:
            data = g.dump()
            log = []
            GradedItem.objects.sync(data, log, course=g.course)
            self.assertEqual(log, [])

    def test_sync_create(self):
        g = GradedItem.objects.filter(parent=None)[:1][0]
        c = g.course
        nm = g.name
        data = g.dump()
        g.delete()
        log = []
        GradedItem.objects.sync(data, log, course=c)
        self.assertEqual(log[0], 'Creating %s: %s' % (c.tag, nm))
        g = GradedItem.objects.get(course=c, parent=None)
        # This assertion relies on ordering entities same way every
        # time.. the `ordering` Meta option of GradedItem and Score is
        # essential.
        self.assertEqual(data, g.dump())
