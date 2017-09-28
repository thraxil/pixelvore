from django.contrib.syndication.views import Feed
from .models import Image
import random


class LatestImagesFeed(Feed):
    title = "Pixelvore"
    link = "/"
    description = "newest images from pixelvore.thraxil.org"

    def items(self):
        return Image.objects.order_by("-created")[:20]

    def item_title(self, item):
        return "image %d" % item.id

    def item_description(self, item):
        return """<a href="%s"><img src="%s" /></a>""" % (
            item.get_absolute_url(),
            item.get_stream_url())


class RandomImagesFeed(Feed):
    title = "Pixelvore"
    link = "/"
    description = "random images from pixelvore.thraxil.org"

    def items(self):
        q = Image.objects.all()
        count = q.count()
        offsets = [random.randint(0, count) for r in range(10)]
        for offset in offsets:
            yield q[offset]

    def item_title(self, item):
        return "image %d" % item.id

    def item_description(self, item):
        return """<a href="%s"><img src="%s" /></a>""" % (
            item.get_absolute_url(),
            item.get_stream_url())
