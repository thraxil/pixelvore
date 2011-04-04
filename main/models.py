from django.conf import settings
from simplejson import loads, dumps

from riak import RiakClient
from riak import RiakPbcTransport
from riak import RiakHttpTransport
from riak import RiakMapReduce

from datetime import datetime
import re
import uuid
import urllib2

HOST = settings.RIAK_HOST
PORT = settings.RIAK_PORT

client = RiakClient(host=HOST,port=PORT)
RIAK_KEYSPACE = "pixelvore"
IMAGE_BUCKET_NAME = RIAK_KEYSPACE + "-image"
THUMB_BUCKET_NAME = RIAK_KEYSPACE + "-thumb"
TAG_BUCKET_NAME = RIAK_KEYSPACE + "-tag"
INDEX_BUCKET_NAME = RIAK_KEYSPACE + "-index"

image_bucket = client.bucket(IMAGE_BUCKET_NAME)
thumb_bucket = client.bucket(THUMB_BUCKET_NAME)
tag_bucket = client.bucket(TAG_BUCKET_NAME)
# since it's inefficient to list all the items
# in a bucket, we manually index some things
index_bucket = client.bucket(INDEX_BUCKET_NAME)

DTFORMAT = "%Y-%m-%dT%H:%M:%S"

class Image(object):
    """ a little wrapper to make things easier to deal
    with from the templates and the rest of django """
    def __init__(self,riakobj):
        self._riakobj = riakobj
        self.slug = riakobj.get_key()
        d = loads(riakobj.get_data())
        self.url = d['url']
        self.created = datetime.strptime(d['created'],DTFORMAT)
        self._thumbs = None

    def get_absolute_url(self):
        return "/image/%s/" % self.slug

    def thumbs(self):
        if self._thumbs is not None:
            return self._thumbs

        self._thumbs = [Thumb(t.get_binary()) for t in self._riakobj.get_links() if t.get().exists()]
        return self._thumbs

    def get_thumb_url(self,size):
        for t in self.thumbs():
            if t.size == size:
                return t.url()
        return None

    def get_full_url(self):
        return self.get_thumb_url("full")

    def get_stream_url(self):
        return self.get_thumb_url("1000")

class Thumb(object):
    def __init__(self,riakobj):
        self.riakobj = riakobj
        d = loads(riakobj.get_data())
        self.size = d['size']
        self.created = datetime.strptime(d['created'],DTFORMAT)
        self.cap = d['cap']
    def url(self):
        return settings.PUBLIC_TAHOE_BASE + "file/" + urllib2.quote(self.cap) + "/?@@named=%s.jpg" % str(self.size)


def slugify(v):
    return re.sub(r'[^A-Za-z0-9]',':',v)

def create_indices():
    index_bucket.new_binary('image-index',"{}").store()
    index_bucket.new_binary('tag-index',"{}").store()

def delete_everything():
    """ for clearing things out """
    imgindex = index_bucket.get_binary("image-index")
    for img in imgindex.get_links():
        i = img.get_binary()
        imgindex.remove_link(i).store()
        i.delete()
 
def index_item(idx,item):
    index = index_bucket.get_binary(idx + "-index")
    index.add_link(item).store()

def deindex_item(idx,item):
    index = index_bucket.get_binary(idx + "-index")
    index.remove_link(item).store()

def create_image(url):
    created = datetime.now().strftime(DTFORMAT)
    slug = str(uuid.uuid4())
    data = {
        'url' : url,
        'created' : created,
        }
    image = image_bucket.new_binary(slug,dumps(data)).store()
    index_item('image',image)
    return slug

def get_image(slug):
    return image_bucket.get_binary(slug)

def get_all_images(limit=None):
    index = index_bucket.get_binary("image-index")
    images = [Image(i) for i in [img.get_binary() for img in index.get_links()] if i.exists()]
    images.sort(key=lambda x: x.created)
    images.reverse()
    if limit is None:
        limit = len(images)
    return images[:limit]

def add_thumb(slug,size,cap):
    created = datetime.now().strftime(DTFORMAT)
    image = get_image(slug)
    data = {
        'size' : size,
        'cap' : cap,
        'created' : created,
        }
    key = str(uuid.uuid4())
    thumb = thumb_bucket.new_binary(key,dumps(data))
    thumb.store()
    image.add_link(thumb)
    image.store()
