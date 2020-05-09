# flake8: noqa
from .settings_shared import *
import os

TEMPLATE_DIRS = (
        os.path.join(os.path.dirname(__file__), "templates"),
)

MEDIA_ROOT = '/var/www/pixelvore/uploads/'

STATICFILES_DIRS = ()
STATIC_ROOT = os.path.join(os.path.dirname(__file__), "../media")

DEBUG = False
TEMPLATE_DEBUG = DEBUG

AWS_S3_CUSTOM_DOMAIN = "d18gpprm4r04fx.cloudfront.net"
AWS_IS_GZIPPED = True

AWS_STORAGE_BUCKET_NAME = "thraxil-pixelvore-static-prod"
AWS_PRELOAD_METADATA = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3Boto3Storage'
S3_URL = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN
STATIC_URL = 'https://%s/media/' % AWS_S3_CUSTOM_DOMAIN
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
MEDIA_URL = S3_URL + '/media/'
COMPRESS_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_QUERYSTRING_AUTH = False


if 'migrate' not in sys.argv:
    INSTALLED_APPS = INSTALLED_APPS + [
        'raven.contrib.django.raven_compat',
    ]

try:
    from local_settings import *
except ImportError:
    pass
