from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from pixelvore.main.feeds import LatestImagesFeed, RandomImagesFeed
import os.path
admin.autodiscover()
import staticmedia

site_media_root = os.path.join(os.path.dirname(__file__),"../media")

urlpatterns = patterns(
    '',
    (r'^$','pixelvore.main.views.index'),
    (r'^feeds/newest/$',LatestImagesFeed()),
    (r'^feeds/random/$',RandomImagesFeed()),
    (r'^scroll/(?P<offset>\d+)/$','pixelvore.main.views.scroll'),
    (r'^import/$','pixelvore.main.views.import_url'),
    (r'^tag/$','pixelvore.main.views.tag_index'),
    (r'^tag/(?P<tag>[^/]+)/$','pixelvore.main.views.tag'),
    (r'^random/$','pixelvore.main.views.random_image'),
    (r'^image/(?P<image_id>[^/]+)/$','pixelvore.main.views.image'),
    (r'^munin/',include('munin.urls')),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
) + staticmedia.serve()

