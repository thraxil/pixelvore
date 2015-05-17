#!/bin/bash

cd /var/www/pixelvore/pixelvore/
exec python manage.py celery beat --settings=pixelvore.settings_docker
