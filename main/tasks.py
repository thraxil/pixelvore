import models
from celery.decorators import task
from restclient import GET,POST
from django.conf import settings
import urllib2
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import cStringIO
import os
import Image
import uuid
import re
from datetime import datetime
from simplejson import loads

def square_resize(img,size):
    sizes = list(img.size)
    trim = abs(sizes[1] - sizes[0]) / 2
    if sizes[0] < sizes[1]:
        img = img.crop((0,trim,sizes[0],trim + sizes[0]))
    if sizes[1] < sizes[0]:
        img = img.crop((trim,0,trim + sizes[1],sizes[1]))
    return img.resize((size,size),Image.ANTIALIAS)    

def resize(img,size=100,square=False):
    if square:
        img = square_resize(img,size)
    else:
        img.thumbnail((size,size),Image.ANTIALIAS)

    # workaround for PIL bug
    if img.size[0] == 0:
        img = img.resize((1,img.size[1]))
    if img.size[1] == 0:
        img = img.resize((img.size[0],1))
        
    return img

@task(ignore_result=True)
def ingest_image(image_id,url):
    print "ingesting %s" % url
    if " " in url:
        url = url.replace(" ","%20")
    filename = url.split("/")[-1]
    if "?" in filename:
        filename = re.sub(r'(\?.*)$','',filename)
    if "#" in filename:
        filename = re.sub(r'(\#.*)$','',filename)

    imgdata = GET(url)
    ext = ".jpg"
    try:
        ext = "." + filename.split(".")[-1].lower()
    except:
        # bad filename
        pass

    ouuid = str(uuid.uuid4())
    filename = ouuid + ext
    tmpfilename = "/var/www/pixelvore/tmp/%s" % filename
    f = open(tmpfilename, "wb")
    f.write(imgdata)
    f.close()

    for size in settings.THUMB_SIZES:
        create_thumb.delay(image_id,tmpfilename,size)

@task(ignore_result=True)
def create_thumb(image_id,tmpfilename,size):
    print "create_thumb %s %s" % (tmpfilename,str(size))
    (dim,sq) = size
    sizestr = "%s%s" % (dim,sq)
    (base,ext) = os.path.splitext(tmpfilename)
    ext = ext.lower()
    if ext not in [".jpg",".gif",".png",".jpeg"]:
        # something weird. just go with jpg
        ext = ".jpg"
    base = base + "_" + sizestr
    thumb_tmpfilename = base + ext
    if dim != "full":
        # make a thumb
        dim = int(dim)
        sq = sq == "square"
        im = Image.open(tmpfilename)
        im = resize(im,dim,sq)
        im.save(thumb_tmpfilename)
    else:
        # don't need to make a _full one
        thumb_tmpfilename = tmpfilename
    upload_thumb.delay(image_id,thumb_tmpfilename,size)

def make_date_directory():
    date = datetime.now()
    path = "%04d/%02d/%02d" % (date.year, date.month, date.day)
    return makedirs(path)

def info(cap):
    return loads(GET(json_url(cap)))

def json_url(cap):
    return settings.TAHOE_BASE + "uri/" + urllib2.quote(cap) + "/?t=json"

def tahoe_url(cap):
    return settings.TAHOE_BASE + "uri/" + urllib2.quote(cap) + "/"

def mkdir(cap,name):
    return POST(tahoe_url(cap),
                params=dict(t="mkdir",
                            name=name),
                async=False)

def get_children(cap):
    return info(cap)[1]['children']

def makedirs(path):
    """ styled after os.makedirs, creates all the directories for the full path"""
    """ expects a rooted path like '/a/b/c' and returns the cap for 'c' """
    def md(cap,path):
        if path == "":
            return cap 
        parts = path.split("/")
        first_child = parts[0]
        rest = parts[1:]

        children = get_children(cap)
        if children.has_key(parts[0]):
            child_info = children[parts[0]]
            child_cap = child_info[1]["rw_uri"]
        else:
            child_cap = mkdir(cap,parts[0])

        return md(child_cap,"/".join(rest))
    dircap = md(settings.TAHOE_BASE_CAP,path)
    return dircap

@task(ignore_result=True)
def upload_thumb(image_id,tmpfilename,size):
    size = "%s%s" % (size[0],size[1])
    print "upload_thumb %s %s" % (tmpfilename,size)

    dircap = make_date_directory()

    source_file = open(tmpfilename,"rb")
    register_openers()
    datagen, headers = multipart_encode((
            ("t","upload"),
            MultipartParam(name='file',fileobj=source_file,
                           filename=os.path.basename(tmpfilename))))
    upload_url = tahoe_url(dircap)
    request = urllib2.Request(upload_url, datagen, headers)
    cap = urllib2.urlopen(request).read()
    source_file.close()

    print cap
    (_p,ext) = os.path.splitext(tmpfilename)
    models.add_thumb(image_id,size,cap,ext)
    # ought to be safe to delete the local copy now
    try:
        os.remove(tmpfilename)
    except:
        pass


