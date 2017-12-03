from django.conf import settings
from json import loads
import re
from django.db import models

DTFORMAT = "%Y-%m-%dT%H:%M:%S"


class Image(models.Model):
    created = models.DateTimeField(auto_now=True)
    url = models.URLField(default="")
    ahash = models.CharField(max_length=256, default="", null=True)
    ext = models.CharField(max_length=256, default=".jpg")

    def get_absolute_url(self):
        return "/image/%d/" % self.id

    def get_full_url(self):
        return "%simage/%s/full/%d%s" % (
            settings.RETICULUM_BASE, self.ahash, self.id, self.ext)

    def get_stream_url(self):
        return "%simage/%s/1000w/%d%s" % (
            settings.RETICULUM_BASE, self.ahash, self.id, self.ext)

    def get_squarethumb_url(self):
        return "%simage/%s/100s/%d%s" % (
            settings.RETICULUM_BASE, self.ahash, self.id, self.ext)

    def tags(self):
        return [it.tag for it in self.imagetag_set.all().order_by("tag__tag")]


class Tag(models.Model):
    slug = models.SlugField()
    tag = models.CharField(max_length=256, default="")


class ImageTag(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


def slugify(title=""):
    title = title.strip().lower()
    slug = re.sub(r"[\W\-]+", "-", title)
    slug = re.sub(r"^\-+", "", slug)
    slug = re.sub(r"\-+$", "", slug)
    return slug


def create_image(url, tags):
    image = Image.objects.create(url=url)
    for tag in tags:
        if not tag:
            continue
        tagslug = slugify(tag)
        if not tagslug:
            # can't tag just punctuation or spaces
            continue
        (t, created) = Tag.objects.get_or_create(slug=tagslug, tag=tag)
        (it, created) = ImageTag.objects.get_or_create(image=image, tag=t)
    return image.id


def get_all_tags():
    return Tag.objects.all().order_by("tag")


def reticulum_save_image(image_id, ahash, ext):
    image = Image.objects.get(id=image_id)
    image.ahash = ahash
    image.ext = ext
    image.save()


def load_everything(filename):
    d = loads(open(filename, "r").read())
    for s in d['images']:
        image = Image.objects.create(url=s['url'], created=s['created'])
        for tag in s['tags']:
            if not tag:
                continue
            tagslug = slugify(tag)
            if not tagslug:
                # can't tag just punctuation or spaces
                continue
            (t, created) = Tag.objects.get_or_create(slug=tagslug, tag=tag)
            (it, created) = ImageTag.objects.get_or_create(image=image, tag=t)
