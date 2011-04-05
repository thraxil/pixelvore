import models
from celery.decorators import task
from restclient import GET
from django.conf import settings
import urllib2
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import cStringIO
import os
import Image

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
def ingest_image(slug,url,current_page):
    print "ingesting %s" % url
    filename = url.split("/")[-1]
    imgdata = GET(url)
    tmpfilename = "/tmp/%s" % filename
    f = open(tmpfilename, "wb")
    f.write(imgdata)
    f.close()

    for size in settings.THUMB_SIZES:
        create_thumb.delay(slug,tmpfilename,size,current_page)

@task(ignore_result=True)
def create_thumb(slug,tmpfilename,size,current_page):
    print "create_thumb %s %s" % (tmpfilename,str(size))
    (dim,sq) = size
    sizestr = "%s%s" % (dim,sq)
    (base,ext) = os.path.splitext(tmpfilename)
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
    upload_thumb.delay(slug,thumb_tmpfilename,size,current_page)


@task(ignore_result=True)
def upload_thumb(slug,tmpfilename,size,current_page):
    size = "%s%s" % (size[0],size[1])
    print "upload_thumb %s %s" % (tmpfilename,size)

    source_file = open(tmpfilename,"rb")
    register_openers()
    datagen, headers = multipart_encode((
            ("t","upload"),
            MultipartParam(name='file',fileobj=source_file,
                           filename=os.path.basename(tmpfilename))))
    request = urllib2.Request(settings.TAHOE_UPLOAD_BASE, datagen, headers)
    cap = urllib2.urlopen(request).read()
    source_file.close()

    print cap
    (_p,ext) = os.path.splitext(tmpfilename)
    models.add_thumb(slug,size,cap,ext,current_page)


