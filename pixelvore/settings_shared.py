# Django settings for pixelvore project.
import os.path
from thraxilsettings.shared import common
import djcelery

app = 'pixelvore'
base = os.path.dirname(__file__)

locals().update(common(app=app, base=base))
djcelery.setup_loader()

INSTALLED_APPS += [  # noqa
    'djcelery',
    'pixelvore.main',
]
CELERYD_CONCURRENCY = 4

RETICULUM_BASE = "https://d2f33fmhbh7cs9.cloudfront.net/"
RETICULUM_UPLOAD_BASE = "https://reticulum.thraxil.org/"
ALLOWED_HOSTS += ['.thraxil.org']  # noqa
