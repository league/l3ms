from django import template

register = template.Library()

@register.filter
def enrolled_in(user, course):
    return(hasattr(user, 'enrollment_set') and
           user.enrollment_set.filter(course=course).count() > 0)

@register.filter
def roster_list(enrollments, id):
    t = template.loader.get_template('courses/roster.html')
    c = template.Context({'id': id,
                          'users': [e.user for e in enrollments],
                          'size': 32})
    return t.render(c)
