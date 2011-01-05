# l3ms.email_validation.views    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from models import ValidationKey
from l3ms.utils import except404

@except404([ValidationKey.DoesNotExist])
def validate(request, key):
    """Respond to a validation link by dispatching to handler.

    The handler must be responsible for deleting `k` from the
    database."""
    k = ValidationKey.objects.get(key=key)
    return ValidationKey.objects.dispatch(request, k)

if settings.DEBUG:
    def x_handler(request, k):
        r = HttpResponse('validated %s' % k)
        k.delete()
        return r
    ValidationKey.objects.register(
        'X', 'X subject',
        'email/test.txt',
        x_handler, 10
        )

@except404([User.DoesNotExist])
def test(request, code, user, email):
    assert settings.DEBUG
    user = User.objects.get(id=user)
    k = ValidationKey.objects.create(request.build_uri, email, user, code)
    return HttpResponse('sent %s' % k)
