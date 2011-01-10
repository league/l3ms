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
