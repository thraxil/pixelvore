from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path
admin.autodiscover()
import staticmedia

site_media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^$','main.views.index'),
                       (r'^scroll/(?P<offset>\d+)/$','main.views.scroll'),
                       (r'^import/$','main.views.import_url'),
                       (r'^tag/$','main.views.tag_index'),
                       (r'^tag/(?P<tag>[^/]+)/$','main.views.tag'),
                       (r'^random/$','main.views.random_image'),
                       (r'^image/(?P<image_id>[^/]+)/$','main.views.image'),
                       (r'^munin/',include('munin.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
) + staticmedia.serve()

