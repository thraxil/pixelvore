from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/pixelvore/pixelvore/templates",
)

MEDIA_ROOT = '/var/www/pixelvore/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/pixelvore/pixelvore/sitemedia'),	
)


DEBUG = False
TEMPLATE_DEBUG = DEBUG
RIAK_HOST = "184.106.204.246"
BROKER_HOST = "184.106.204.246"

try:
    from local_settings import *
except ImportError:
    pass
