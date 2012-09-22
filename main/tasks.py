import models
from celery.decorators import task
from restclient import GET,POST
from django.conf import settings
import cStringIO
import os
import uuid
import re
from datetime import datetime
from simplejson import loads
import requests


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

    files = {'image': ("image" + ext, imgobj) }
    r = requests.post(RETICULUM_BASE, files=files)
    rhash = loads(r.text)["hash"]
    print " uploaded to reticulum %s" % rhash
    models.reticulum_save_image(image_id,rhash,ext)

