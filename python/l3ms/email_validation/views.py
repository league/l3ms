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
    r = ValidationKey.objects.dispatch(request, k)
    k.delete()
    return r

if DEBUG:
    def x_handler(request, k):
        return HttpResponse('validated %s' % k)
    ValidationKey.objects.register(
        'X', 'X subject',
        'email-validation/test.txt',
        x_handler, 10
        )

def test(request, code, user, email):
    try:
        user = User.objects.get(id=user)
    except User.DoesNotExist:
        raise Http404
    k = ValidationKey.objects.create(request, email, user, code)
    return HttpResponse('sent %s' % k)
