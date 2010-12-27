# Create your views here.

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

def dict_to_ul(d):
    buf = '<ul>'
    for k,v in d.items():
        buf += '<li><b>'+k+' =</b> '+str(v)+'</li>'
    buf += '</ul>'
    return buf

@login_required
def hello(request):
    buf = request.user.username
    buf += '<br>'
    buf += reverse(hello)
    buf += '<br>'
    buf += reverse('django.contrib.auth.views.login')
    buf += '<h1>META</h1>'
    buf += dict_to_ul(request.META)
    buf += '<h1>environ</h1>'
    buf += dict_to_ul(request.environ)
    return HttpResponse(buf)

