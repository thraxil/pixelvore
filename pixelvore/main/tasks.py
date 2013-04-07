import pixelvore.main.models as models
from celery.decorators import task
import requests
from django.conf import settings
import cStringIO
import re
from simplejson import loads


@task(ignore_result=True)
def ingest_image(image_id, url):
    print "ingesting %s" % url
    if " " in url:
        url = url.replace(" ", "%20")
    filename = url.split("/")[-1]
    if "?" in filename:
        filename = re.sub(r'(\?.*)$', '', filename)
    if "#" in filename:
        filename = re.sub(r'(\#.*)$', '', filename)

    r = requests.get(url)

    ext = ".jpg"
    try:
        ext = "." + filename.split(".")[-1].lower()
    except:
        # bad filename
        pass

    imgobj = cStringIO.StringIO()
    for chunk in r.iter_content(1024):
        imgobj.write(chunk)
    imgobj.seek(0)

    files = {'image': ("image" + ext, imgobj)}
    r = requests.post(settings.RETICULUM_BASE, files=files)
    rhash = loads(r.text)["hash"]
    print " uploaded to reticulum %s" % rhash
    models.reticulum_save_image(image_id, rhash, ext)
