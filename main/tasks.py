import models
from celery.decorators import task
from restclient import GET,POST
from django.conf import settings
import urllib2
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import cStringIO
import os
import Image
import uuid
import re
from datetime import datetime
from simplejson import loads

@task(ignore_result=True)
def ingest_image(image_id,url):
    print "ingesting %s" % url
    if " " in url:
        url = url.replace(" ","%20")
    filename = url.split("/")[-1]
    if "?" in filename:
        filename = re.sub(r'(\?.*)$','',filename)
    if "#" in filename:
        filename = re.sub(r'(\#.*)$','',filename)

    imgdata = GET(url)
    ext = ".jpg"
    try:
        ext = "." + filename.split(".")[-1].lower()
    except:
        # bad filename
        pass

    imgobj = cStringIO.StringIO()
    imgobj.write(imgdata)
    imgobj.seek(0)

    register_openers()
    datagen, headers = multipart_encode((
            ("t","upload"),
            MultipartParam(name='image',fileobj=imgobj,
                           filename="image%s" % ext)))
    request = urllib2.Request("http://apomixis.thraxil.org/", datagen, headers)
    metadata = loads(urllib2.urlopen(request).read())
    print " uploaded to apomixis %s" % metadata["hash"]
    models.apomixis_save_image(image_id,metadata["hash"],metadata["extension"])

