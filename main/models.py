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
PAGE_BUCKET_NAME = RIAK_KEYSPACE + "-page"

image_bucket = client.bucket(IMAGE_BUCKET_NAME)
thumb_bucket = client.bucket(THUMB_BUCKET_NAME)
tag_bucket = client.bucket(TAG_BUCKET_NAME)
page_bucket = client.bucket(PAGE_BUCKET_NAME)

# since it's inefficient to list all the items
# in a bucket, we manually index some things
index_bucket = client.bucket(INDEX_BUCKET_NAME)

PAGE_SIZE = 10

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

        self._thumbs = [Thumb(t.get_binary()) for t in self._riakobj.get_links() \
                            if t.get().exists() and t.get_bucket() == THUMB_BUCKET_NAME]
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

    def tags(self):
        return [t.get_key() for t in self._riakobj.get_links() if t.get().exists() and t.get_bucket() == TAG_BUCKET_NAME]

class Thumb(object):
    def __init__(self,riakobj):
        self.riakobj = riakobj
        d = loads(riakobj.get_data())
        self.size = d['size']
        self.created = datetime.strptime(d['created'],DTFORMAT)
        self.cap = d['cap']
        self.ext = d.get('ext','.jpg')
    def url(self):
        return settings.PUBLIC_TAHOE_BASE + "file/" + urllib2.quote(self.cap) + "/?@@named=%s%s" % (str(self.size),self.ext)


def slugify(v):
    return re.sub(r'[^A-Za-z0-9]',':',v)

def create_indices():
    index_bucket.new_binary('image-index',"{}").store()
    index_bucket.new_binary('tag-index',"{}").store()
    index_bucket.new_binary('page-index',"{}").store()
    index_bucket.new_binary('current-page',"0").store()

def delete_everything():
    """ for clearing things out """
    imgindex = index_bucket.get_binary("image-index")
    for img in imgindex.get_links():
        i = img.get_binary()
        imgindex.remove_link(i).store()
        i.delete()
    for p in pageindex.get_links():
        page = p.get_binary()
        pageindex.remove_link(i).store()
        page.delete()
 
def index_item(idx,item):
    index = index_bucket.get_binary(idx + "-index")
    index.add_link(item).store()

def deindex_item(idx,item):
    index = index_bucket.get_binary(idx + "-index")
    index.remove_link(item).store()

def create_image(url,tags):
    created = datetime.now().strftime(DTFORMAT)
    slug = str(uuid.uuid4())
    data = {
        'url' : url,
        'created' : created,
        }
    image = image_bucket.new_binary(slug,dumps(data)).store()
    index_item('image',image)
    tagindex = index_bucket.get_binary('tag-index')
    for tag in tags:
        if not tag:
            continue
        t = tag_bucket.get_binary(slugify(tag))
        if not t.exists():
            t = tag_bucket.new(slugify(tag),tag).store()
            t.add_link(image).store()
            image.add_link(t).store()
            tagindex.add_link(t).store()
        else:
            image.add_link(t).store()
            t.add_link(image).store()
            
    return slug

def get_image(slug):
    return image_bucket.get_binary(slug)

def get_image_obj(slug):
    return Image(get_image(slug))

def get_all_images(limit=None):
    # TODO: sort the images by date without having to instantiate objects
    # ie, use the map-reduce framework
    index = index_bucket.get_binary('image-index')
    images = [Image(i) for i in [img.get_binary() for img in index.get_links()] if i.exists()]
    images.sort(key=lambda x: x.created)
    images.reverse()
    if limit is None:
        limit = len(images)
    return images[:limit]

def get_all_tags():
    tagindex = index_bucket.get_binary('tag-index')
    tags = [str(t.get().get_data()) for t in tagindex.get_links() if t.get().exists()]
    tags.sort(key=str.lower)
    return tags


def get_tag_images(tag):
    t = tag_bucket.get_binary(tag)
    if not t.exists():
        return []

    return [Image(i.get_binary()) for i in t.get_links() if i.get_bucket() == IMAGE_BUCKET_NAME and i.get().exists()]

def add_thumb(slug,size,cap,ext,current_page):
    created = datetime.now().strftime(DTFORMAT)
    image = get_image(slug)
    data = {
        'size' : size,
        'cap' : cap,
        'created' : created,
        'ext' : ext,
        }
    key = str(uuid.uuid4())
    thumb = thumb_bucket.new_binary(key,dumps(data))
    thumb.store()
    image.add_link(thumb)
    image.store()
    if size == "1000":
        # TODO: figure out something more efficient
        # so we don't have to update *all* the pages
        # each time an image is added
        update_pages(current_page)

def clear_orphan_images():
    imageindex = index_bucket.get_binary('image-index')
    for ilink in imageindex.get_links():
        if ilink.get().exists():
            img = ilink.get()
            image = Image(img)
            url = image.get_stream_url()
            if not url:
                imageindex.remove_link(ilink).store()
                img.delete()
        else:
            imageindex.remove_link(ilink.get()).store()
    delete_all_pages()
    update_pages()
            
def delete_all_pages():
    for i in range(int(index_bucket.get_binary("current-page").get_data())):
        p = page_bucket.get(str(i)).delete()
    index_bucket.get_binary("current-page").set_data("0").store()    


def update_pages(start_at=0):
    imageindex = index_bucket.get_binary('image-index')

    images = [Image(i) for i in [img.get_binary() for img in imageindex.get_links()] if i.exists()]
    images.sort(key=lambda x: x.created)

    image_count = len(images)
    page_number = int(index_bucket.get_binary("current-page").get_data())

    for i in range(image_count):
        if i >= start_at:
            make_page_image(i,images[i])

    current_image = page_number * PAGE_SIZE

def make_page_image(i,image):
    p = page_bucket.get(str(i))
    if not p.exists():
        p = page_bucket.new(str(i),
                            dict(slug=image.slug,
                                 thumb_url=image.get_stream_url())
                            ).store()
    else:
        p.set_data(
            dict(slug=image.slug,
                 thumb_url=image.get_stream_url())
            ).store()

    cp = int(index_bucket.get_binary("current-page").get_data())
    if i > cp:
        index_bucket.get_binary("current-page").set_data(str(i)).store()

def get_current_page():
    return int(index_bucket.get_binary("current-page").get_data())

def get_pages(limit=10,offset=0):
    current_page = get_current_page()
    pages = range(current_page + 1)
    pages.reverse()
    for p in pages[offset:limit+offset]:
        pg = page_bucket.get(str(p)).get_data()
        yield pg
        
