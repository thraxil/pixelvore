from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
import models
import tasks
from utils import parse_tags
from restclient import GET
import html5lib
from html5lib import treebuilders
import re

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
    limit = int(request.GET.get('limit','50'))
    return dict(images=models.get_all_images(limit))

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

@rendered_with("main/import.html")
def import_url(request):
    if request.method == "GET":
        url = request.GET.get('url','')
        resp,data = GET(url,resp=True)
        if resp['status'] != '200':
            return HttpResponse("couldn't fetch it. sorry")

        if resp['content-type'].startswith('image/'):
            return dict(url=url)
        elif resp['content-type'].startswith('text/html'):
            parser=html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
            tree = parser.parse(data)
            images = [i for i in tree.findAll('img') if get_width(i) > 75]
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

        for url in urls:
            slug = models.create_image(url=url)
            tasks.ingest_image.delay(slug,url)
        return HttpResponseRedirect("/")
