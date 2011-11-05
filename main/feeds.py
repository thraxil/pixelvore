from django.contrib.syndication.views import Feed
import models
import random

class LatestImagesFeed(Feed):
    title = "Pixelvore"
    link = "/"
    description = "newest images from pixelvore.thraxil.org"

    def items(self):
        return models.Image.objects.order_by("-created")[:20]

    def item_title(self, item):
        return "image %d" % item.id

    def item_description(self, item):
        return """<a href="%s"><img src="%s" /></a>""" % (item.get_absolute_url(),
                                                          item.get_stream_url())


class RandomImagesFeed(Feed):
    title = "Pixelvore"
    link = "/"
    description = "random images from pixelvore.thraxil.org"

    def items(self):
        q = models.Thumb.objects.filter(size="1000")
        count = q.count()
        offsets = [random.randint(0,count) for r in range(10)]
        for offset in offsets:
            t = q[offset]
            yield t.image

    def item_title(self, item):
        return "image %d" % item.id

    def item_description(self, item):
        return """<a href="%s"><img src="%s" /></a>""" % (item.get_absolute_url(),
                                                          item.get_stream_url())
