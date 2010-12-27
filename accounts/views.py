from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def profile(request):
    return HttpResponse('Hello, '+ request.user.username)

