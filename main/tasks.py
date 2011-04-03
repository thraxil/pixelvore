import models
from celery.decorators import task
from restclient import GET
from django.conf import settings
import urllib2
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import cStringIO

@task(ignore_result=True)
def ingest_image(slug,url):
    print "ingesting %s" % url
    filename = url.split("/")[-1]
    print filename
    imgdata = GET(url)
    dfile = cStringIO.StringIO()
    dfile.write(imgdata)
    dfile.seek(0)

    register_openers()
    datagen, headers = multipart_encode({
            "t" : "upload",
            "file" : dfile,
            })
    print str(headers)
    tahoe_url = settings.TAHOE_UPLOAD_BASE
    request = urllib2.Request(tahoe_url, datagen, headers)
    cap = urllib2.urlopen(request).read()
    print cap
    models.add_thumb(slug,"full",cap)
    # TODO: other sizes
