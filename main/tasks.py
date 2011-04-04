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




    tmpfilename = "/tmp/%s" % filename
    f = open(tmpfilename, "wb")
    f.write(imgdata)
    f.close()


    source_file = open(tmpfilename,"rb")
    register_openers()
    datagen, headers = multipart_encode((
            ("t","upload"),
            MultipartParam(name='file',fileobj=source_file,
                           filename=filename)))
    request = urllib2.Request(settings.TAHOE_UPLOAD_BASE, datagen, headers)
    cap = urllib2.urlopen(request).read()
    source_file.close()

    print cap
    models.add_thumb(slug,"full",cap)
    # TODO: other sizes
