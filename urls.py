from django.conf.urls.defaults import *
import djlms.misc.views
from djlms.settings import PREFIX

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^'+PREFIX+r'misc/$', djlms.misc.views.hello),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^'+PREFIX+r'admin/', include(admin.site.urls)),
)
