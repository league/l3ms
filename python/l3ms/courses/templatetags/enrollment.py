from django import template

register = template.Library()

@register.filter
def enrolled_in(user, course):
    return(hasattr(user, 'enrollment_set') and
           user.enrollment_set.filter(course=course).count() > 0)
