# Django settings for pixelvore project.
import os.path
from thraxilsettings.shared import common

app = 'pixelvore'
project = app
base = os.path.dirname(__file__)

locals().update(common(app=app, base=base))

INSTALLED_APPS += [  # noqa
    'pixelvore.main',
    'raven.contrib.django.raven_compat',
]
CELERYD_CONCURRENCY = 4

RETICULUM_BASE = "https://d2f33fmhbh7cs9.cloudfront.net/"
RETICULUM_UPLOAD_BASE = "https://reticulum.thraxil.org/"
ALLOWED_HOSTS += ['.thraxil.org']  # noqa

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
