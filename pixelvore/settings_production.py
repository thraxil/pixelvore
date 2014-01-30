# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/pixelvore/pixelvore/pixelvore/templates",
)

MEDIA_ROOT = '/var/www/pixelvore/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/pixelvore/pixelvore/sitemedia'),
)

STATICFILES_DIRS = ()
STATIC_ROOT = "/var/www/skinflint/skinflint/media/"

DEBUG = False
TEMPLATE_DEBUG = DEBUG

if 'migrate' not in sys.argv:
    INSTALLED_APPS = INSTALLED_APPS + [
        'raven.contrib.django.raven_compat',
    ]

try:
    from local_settings import *
except ImportError:
    pass
