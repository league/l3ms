# Create your views here.

from django.http import HttpResponse

def dict_to_ul(d):
    buf = '<ul>'
    for k,v in d.items():
        buf += '<li><b>'+k+' =</b> '+str(v)+'</li>'
    buf += '</ul>'
    return buf

def hello(request):
    buf = '<h1>META</h1>'
    buf += dict_to_ul(request.META)
    buf += '<h1>environ</h1>'
    buf += dict_to_ul(request.environ)
    return HttpResponse(buf)

