# flake8: noqa
from settings_shared import *
from thraxilsettings.compose import common

locals().update(
    common(
        project=project,
        base=base,
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS,
    ))

CELERY_BROKER_URL = BROKER_URL

try:
    from local_settings import *
except ImportError:
    pass

print(BROKER_URL)
