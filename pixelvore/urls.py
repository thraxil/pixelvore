import django.views.static

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from pixelvore.main.feeds import LatestImagesFeed, RandomImagesFeed
from pixelvore.main.views import (
    index, scroll, import_url, tag_index, tag, random_image, image
)
admin.autodiscover()


urlpatterns = [
    url(r'^$', index),
    url(r'smoketest/', include('smoketest.urls')),
    url(r'^feeds/newest/$', LatestImagesFeed()),
    url(r'^feeds/random/$', RandomImagesFeed()),
    url(r'^scroll/(?P<offset>\d+)/$', scroll),
    url(r'^import/$', import_url),
    url(r'^tag/$', tag_index),
    url(r'^tag/(?P<tag>[^/]+)/$', tag),
    url(r'^random/$', random_image),
    url(r'^image/(?P<image_id>[^/]+)/$', image),
    url(r'^uploads/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
