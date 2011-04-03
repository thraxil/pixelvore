from django.conf import settings
from simplejson import loads, dumps

from riak import RiakClient
from riak import RiakPbcTransport
from riak import RiakHttpTransport
from riak import RiakMapReduce

from datetime import datetime
import re
import uuid

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

def slugify(v):
    return re.sub(r'[^A-Za-z0-9]',':',v)

def create_indices():
    index_bucket.new_binary('image-index',"{}").store()
    index_bucket.new_binary('tag-index',"{}").store()

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

