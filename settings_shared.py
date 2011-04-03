# Django settings for pixelvore project.
import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ( )

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'pixelvore' # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "/var/www/pixelvore/uploads/"
MEDIA_URL = '/uploads/'
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = ')ng#)ef_u@_^zvvu@dxm7q-lyb_^!a6%v3v^j3b(mp+)l+5%@h'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'pixelvore.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__),"templates"),
)

import djcelery
djcelery.setup_loader()

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'staticmedia',
    'sorl.thumbnail',
    'smartif',
    'template_utils',
    'typogrify',
    'munin',
    'djcelery',
    'main',
)

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[pixelvore] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "anders@columbia.edu"

# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', 'sitemedia'),
)

RIAK_HOST = "128.59.152.25"
RIAK_PORT = "8098"

#CELERY_RESULT_BACKEND = "database"
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_VHOST = "/"
CELERYD_CONCURRENCY = 4

TAHOE_BASE = "http://localhost:3456/"
TAHOE_BASE_CAP = "URI:DIR2:tnjkufdxv7lk6zhxnt5jvbc7q4lcyovifvyt3lcd6c2dbpweqzo72x5fnefnui5snwx2qfeui5u46q"

THUMB_SIZES = (
    ("full",""),
    ("1000",""),
    ("100",""),
    ("100","square"),
    ("50","square"),
)
