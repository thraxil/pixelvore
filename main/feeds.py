from django.contrib.syndication.views import Feed
import models

class LatestImagesFeed(Feed):
    title = "Pixelvore"
    link = "/"
    description = "newest images from pixelvore.thraxil.org"

    def items(self):
        thumbs = models.Thumb.objects.filter(size="1000").order_by("-created")[:50]
        return [t.image for t in thumbs]

    def item_title(self, item):
        return "image %d" % item.id

    def item_description(self, item):
        return """<a href="%s"><img src="%s" /></a>""" % (item.get_absolute_url(),
                                                          item.get_stream_url())
