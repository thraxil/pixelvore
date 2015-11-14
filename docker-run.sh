#!/bin/bash

cd /var/www/pixelvore/pixelvore/
python manage.py migrate --noinput --settings=pixelvore.settings_docker || exit 1
python manage.py collectstatic --noinput --settings=pixelvore.settings_docker || exit 1
python manage.py compress --settings=pixelvore.settings_docker || exit 1
exec gunicorn --env \
  DJANGO_SETTINGS_MODULE=pixelvore.settings_docker \
  pixelvore.wsgi:application -b 0.0.0.0:8000 -w 3 \
  --access-logfile=- --error-logfile=-
