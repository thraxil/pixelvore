from django.conf import settings
from simplejson import loads, dumps
from datetime import datetime
import re
import uuid
import urllib2
from django.db import models

DTFORMAT = "%Y-%m-%dT%H:%M:%S"



class Image(models.Model):
    created = models.DateTimeField(auto_now=True)
    url = models.URLField(default="")

    def get_absolute_url(self):
        return "/image/%d/" % self.id

    def get_thumb_url(self,size):
        r = self.thumb_set.filter(size=size)
        if r.count() == 1:
            return r[0].url()
        else:
            return None

    def get_full_url(self):
        return self.get_thumb_url("full")

    def get_stream_url(self):
        return self.get_thumb_url("1000")

    def get_squarethumb_url(self):
        return self.get_thumb_url("100square")


    def tags(self):
        return [it.tag for it in self.imagetag_set.all().order_by("tag__tag")]

class Thumb(models.Model):
    image = models.ForeignKey(Image)
    size = models.CharField(max_length=256,default="full")
    created = models.DateTimeField(auto_now=True)
    cap = models.TextField(default="",blank="")
    ext = models.CharField(max_length=256,default=".jpg")

    def url(self):
        return settings.PUBLIC_TAHOE_BASE + "file/" + urllib2.quote(self.cap) + "/?@@named=%s%s" % (str(self.size),self.ext)

    def width(self):
        if self.size.endswith("square"):
            return int(self.size[:-6])
        return None

    def height(self):
        if self.size.endswith("square"):
            return int(self.size[:-6])
        return None


class Tag(models.Model):
    slug = models.SlugField()
    tag = models.CharField(max_length=256,default="")

class ImageTag(models.Model):
    image = models.ForeignKey(Image)
    tag = models.ForeignKey(Tag)

def slugify(title=""):
    title = title.strip().lower()
    slug = re.sub(r"[\W\-]+","-",title)
    slug = re.sub(r"^\-+","",slug)
    slug = re.sub(r"\-+$","",slug)
    return slug


def create_image(url,tags):
    image = Image.objects.create(url=url)
    for tag in tags:
        if not tag:
            continue
        tagslug = slugify(tag)
        if not tagslug:
            # can't tag just punctuation or spaces
            continue
        (t,created) = Tag.objects.get_or_create(slug=tagslug,tag=tag)
        (it,created) = ImageTag.objects.get_or_create(image=image,tag=t)
    return image.id

def get_all_tags():
    return Tag.objects.all().order_by("tag")


def add_thumb(image_id,size,cap,ext):
    image = Image.objects.get(id=image_id)
    thumb = Thumb.objects.create(image=image,size=size,cap=cap,ext=ext)


def load_everything(filename):
    d = loads(open(filename,"r").read())
    for s in d['images']:
        print s['url'], s['created']
        image = Image.objects.create(url=s['url'],created=s['created'])
        for tag in s['tags']:
            if not tag:
                continue
            tagslug = slugify(tag)
            if not tagslug:
                # can't tag just punctuation or spaces
                continue
            (t,created) = Tag.objects.get_or_create(slug=tagslug,tag=tag)
            (it,created) = ImageTag.objects.get_or_create(image=image,tag=t)
        for thumb in s['thumbs']:
            t = Thumb.objects.create(image=image,size=thumb['size'],cap=thumb['cap'],ext=thumb['ext'],
                                     created=thumb['created'])
        print "finished %s" % s['url']
            
