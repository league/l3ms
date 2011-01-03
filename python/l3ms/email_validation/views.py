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
