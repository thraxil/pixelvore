import models
from celery.decorators import task
from restclient import POST,GET
from django.conf import settings

@task(ignore_result=True)
def ingest_image(slug,url):
    print "ingesting %s" % url
    print slug
