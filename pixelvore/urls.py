from django.conf.urls import patterns, include
from django.contrib import admin
from django.conf import settings
from pixelvore.main.feeds import LatestImagesFeed, RandomImagesFeed
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^$', 'pixelvore.main.views.index'),
    (r'^feeds/newest/$', LatestImagesFeed()),
    (r'^feeds/random/$', RandomImagesFeed()),
    (r'^scroll/(?P<offset>\d+)/$', 'pixelvore.main.views.scroll'),
    (r'^import/$', 'pixelvore.main.views.import_url'),
    (r'^tag/$', 'pixelvore.main.views.tag_index'),
    (r'^tag/(?P<tag>[^/]+)/$', 'pixelvore.main.views.tag'),
    (r'^random/$', 'pixelvore.main.views.random_image'),
    (r'^image/(?P<image_id>[^/]+)/$', 'pixelvore.main.views.image'),
    (r'^munin/', include('munin.urls')),
    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),
)
