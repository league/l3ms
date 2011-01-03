# l3ms.email_validation.views    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib.auth.models import User
from django.conf import settings
from django.http import Http404, HttpResponse
from models import ValidationKey
from settings import DEBUG

def validate(request, key):
    try:
        k = ValidationKey.objects.get(key=key)
    except ValidationKey.DoesNotExist:
        raise Http404
    # Handler will be responsible for deleting k
    return ValidationKey.objects.dispatch(request, k)

if DEBUG:
    def x_handler(request, k):
        r = HttpResponse('validated %s' % k)
        k.delete()
        return r
    ValidationKey.objects.register(
        'X', 'X subject',
        'email/test.txt',
        x_handler, 10
        )

def test(request, code, user, email):
    try:
        user = User.objects.get(id=user)
    except User.DoesNotExist:
        raise Http404
    k = ValidationKey.objects.create(request.build_uri, email, user, code)
    return HttpResponse('sent %s' % k)
