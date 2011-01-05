from django import template

register = template.Library()

@register.filter
def gravatar(user, size=80):
    return user.gravatar(size=size)
