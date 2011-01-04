from django.conf.urls.defaults import *
from django.contrib import admin
from settings import URL_PREFIX, DEBUG, PROJECT_ROOT
import accounts.urls
import accounts.views
import email_validation.views
import http_auth.urls

admin.autodiscover()

subpatterns = patterns(
    '',
    url(r'^$', accounts.views.home, name='home'),
    url(r'^u/(?P<username>\w+)$', accounts.views.profile, name='profile'),
    url(r'^validation/(?P<key>.+)$', email_validation.views.validate,
        name='validate'),
    (r'^acct/', include(accounts.urls)),
    (r'^auth/', include(http_auth.urls)),
    (r'^admin/', include(admin.site.urls)),
    )

if DEBUG:
    subpatterns += patterns(
        '',
        url(r'^test/valid/(?P<code>\w)(?P<user>\d+)/(?P<email>.+)$',
            email_validation.views.test, name='test_validation'),
        )

urlpatterns = patterns(
    '',
    (r'^'+URL_PREFIX, include(subpatterns))
    )

if DEBUG:
    from django.views.static import serve
    from os.path import join

    urlpatterns += patterns(
        '',
        (r'^l3media/(?P<path>.*)$', serve,
         {'document_root': join(PROJECT_ROOT, 'static')})
        )
