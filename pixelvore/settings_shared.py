# Django settings for pixelvore project.
import os.path
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pixelvore',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '', }
}

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '', }}


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=pixelvore',
]

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
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'pixelvore.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

import djcelery
djcelery.setup_loader()

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smartif',
    'template_utils',
    'typogrify',
    'munin',
    'djcelery',
    'pixelvore.main',
    'django_nose',
    'south',
    'django_statsd',
    'gunicorn',
)

STATIC_URL = "/media/"
STATICFILES_DIRS = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../media/")),
)
STATIC_ROOT = ""
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[pixelvore] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "anders@columbia.edu"

# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', 'sitemedia'),
)

#CELERY_RESULT_BACKEND = "database"
BROKER_HOST = "128.59.152.25"
BROKER_PORT = 5672
BROKER_VHOST = "/"
CELERYD_CONCURRENCY = 4

RETICULUM_BASE = "http://reticulum.thraxil.org/"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True

STATSD_CLIENT = 'statsd.client'
STATSD_PREFIX = 'pixelvore'
STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125
STATSD_PATCHES = ['django_statsd.patches.db', ]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

ALLOWED_HOSTS = ['localhost', '.thraxil.org']
