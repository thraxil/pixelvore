from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
import models
import tasks
from utils import parse_tags
from restclient import GET
import html5lib
from html5lib import treebuilders
import re
import urlparse
from django.db import transaction


class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if type(items) == type({}):
                return render_to_response(self.template_name, items, context_instance=RequestContext(request))
            else:
                return items

        return rendered_func

@rendered_with("main/index.html")
def index(request):
    limit = int(request.GET.get('limit','10'))
    offset = int(request.GET.get('offset','0'))
    return dict(images=models.Image.objects.all().order_by("-created")[offset:limit+offset])

@rendered_with("main/tag_index.html")
def tag_index(request):
    return dict(tags=models.get_all_tags())

@rendered_with("main/tag.html")
def tag(request,tag):
    t = get_object_or_404(models.Tag,slug=tag)
    return dict(images=[it.image for it in t.imagetag_set.all()],
                tag=t)

@rendered_with("main/image.html")
def image(request,image_id):
    image = get_object_or_404(models.Image,id=image_id)
    return dict(image=image)


def get_width(i):
    if i.has_key('width'):
        return width_parse(i['width'])
    else:
        return 1000

def width_parse(w):
    w = re.sub(r'\D','',w)
    try:
        return int(w)
    except ValueError:
        return 0

def fix_base_path(image,base_url):
    if not image['src'].startswith("http://"):
        image['src'] = urlparse.urljoin(base_url,image['src'])
    return image
        
@transaction.commit_manually
@rendered_with("main/import.html")
def import_url(request):
    if request.method == "GET":
        url = request.GET.get('url','')
        if not url:
            return dict()
        resp,data = GET(url,resp=True)
        if resp['status'] != '200':
            print str(resp['status'])
            return HttpResponse("couldn't fetch it. sorry")

        if resp['content-type'].startswith('image/'):
            return dict(url=url)
        elif resp['content-type'].startswith('text/html'):
            parser=html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
            tree = parser.parse(data)
            images = [fix_base_path(i,url) for i in tree.findAll('img') if get_width(i) > 75]
            return dict(html=True,images=images)
        else:
            return HttpResponse("unknown content-type: %s" % resp['content-type'])
    if request.method == "POST":
        urls = []
        url = request.POST.get('url','')
        if url != '':
            urls = [url]
        else:
            # probably an html page submission
            for k in request.POST.keys():
                if k.startswith("image_"):
                    url = k[len("image_"):]
                    urls.append(url)

        tags = parse_tags(request.POST.get('tags',''))
        pairs = []
        try:
            for url in urls:
                image_id = models.create_image(url=url,tags=tags)
                pairs.append((image_id,url))
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
            for (image_id,url) in pairs:
                tasks.ingest_image.delay(image_id,url)
        return HttpResponseRedirect("/")
