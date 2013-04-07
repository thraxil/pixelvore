from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/pixelvore/pixelvore/pixelvore/templates",
)

MEDIA_ROOT = '/var/www/pixelvore/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/pixelvore/pixelvore/sitemedia'),	
)


DEBUG = False
TEMPLATE_DEBUG = DEBUG

try:
    from local_settings import *
except ImportError:
    pass
