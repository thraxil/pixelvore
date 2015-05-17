#!/bin/bash

cd /var/www/pixelvore/pixelvore/
exec python manage.py celery worker --settings=pixelvore.settings_docker
