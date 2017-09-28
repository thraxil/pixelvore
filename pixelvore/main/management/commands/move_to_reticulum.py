from django.core.management.base import BaseCommand
import main.models
import os.path
import os
from simplejson import loads
import requests

RETICULUM_BASE = "http://behemoth.ccnmtl.columbia.edu:14002/"


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        cnt = 0
        total = main.models.Image.objects.count()
        for i in main.models.Image.objects.all():
            apomixis_url = (
                "http://apomixis.thraxil.org/image/%s/full/%d%s"
                % (i.ahash, i.id, i.ext))
            print(apomixis_url)
            tmpfilename = "/tmp/temp" + i.ext
            os.system("wget %s -O %s" % (apomixis_url, tmpfilename))
            files = {'image': ("image.jpg",
                               open(tmpfilename, 'rb'))
                     }
            r = requests.post(RETICULUM_BASE, files=files)
            rhash = loads(r.text)["hash"]
            if i.ahash != rhash:
                print("hash changed!")
                print(i.ahash, rhash)
                i.ahash = rhash
                i.save()
            print("moved %d of %d" % (cnt, total))
            cnt += 1
