from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
import pixelvore.main.models as models
import pixelvore.main.tasks as tasks
from utils import parse_tags
import requests
from bs4 import BeautifulSoup
import re
import urlparse
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random


class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if isinstance(items, dict):
                return render_to_response(
                    self.template_name, items,
                    context_instance=RequestContext(request))
            else:
                return items

        return rendered_func


@rendered_with("main/index.html")
def index(request):
    limit = int(request.GET.get('limit', '10'))
    offset = int(request.GET.get('offset', '0'))
    images = models.Image.objects.filter(
        ahash__gt="").order_by("-created")[offset:offset + limit]
    for i in images:
        i.offset = offset
        offset += 1
    noffset = offset + limit
    next_page_images = models.Image.objects.filter(
        ahash__gt="").order_by("-created")[noffset:noffset + limit]
    for i in next_page_images:
        i.offset = offset
        offset += 1
    return dict(images=images, next_page_images=next_page_images)


@rendered_with("main/scroll.html")
def scroll(request, offset):
    limit = int(request.GET.get('limit', '10'))
    offset = int(offset) + 1
    images = models.Image.objects.filter(
        ahash__gt="").order_by("-created")[offset:offset + limit]
    for i in images:
        i.offset = offset
        offset += 1
    noffset = offset + limit
    next_page_images = models.Image.objects.filter(
        ahash__gt="").order_by("-created")[noffset:noffset + limit]
    for i in next_page_images:
        i.offset = offset
        offset += 1
    return dict(images=images, next_page_images=next_page_images)


@rendered_with("main/tag_index.html")
def tag_index(request):
    return dict(tags=models.get_all_tags())


def get_single_tag(tag):
    r = models.Tag.objects.filter(slug=tag)
    if r.count() == 0:
        raise Http404
    if r.count() == 1:
        return r.first()
    # multiples! clear out all but one
    for t in list(r)[1:]:
        t.delete()
    return r.first()


@rendered_with("main/tag.html")
def tag(request, tag):
    t = get_single_tag(tag)
    paginator = Paginator(t.imagetag_set.all(), 100)
    page = request.GET.get('page', '1')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)
    return dict(images=images, tag=t)


@rendered_with("main/image.html")
def image(request, image_id):
    image = get_object_or_404(models.Image, id=image_id)
    return dict(image=image)


@rendered_with("main/image.html")
def random_image(request):
    cnt = models.Image.objects.all().count()
    i = random.randint(0, cnt)
    image = models.Image.objects.all()[i]
    return dict(image=image)


def get_width(i):
    if 'width' in i:
        return width_parse(i['width'])
    else:
        return 1000


def width_parse(w):
    w = re.sub(r'\D', '', w)
    try:
        return int(w)
    except ValueError:
        return 0


def fix_base_path(image, base_url):
    if not image['src'].startswith("http://"):
        image['src'] = urlparse.urljoin(base_url, image['src'])
    return image


def fix_link_base_path(link, base_url):
    if not link['href'].startswith("http://"):
        link['href'] = urlparse.urljoin(base_url, link['href'])
    return link


def is_image_link(link):
    if 'href' not in link:
        return False
    return link['href'].lower().endswith(".jpg") or \
        link['href'].lower().endswith(".jpeg") or \
        link['href'].lower().endswith(".png") or \
        link['href'].lower().endswith(".gif")


def import_url_form(request):
    url = request.GET.get('url', '')
    url = url.replace(" ", "%20").replace("+", "%20")
    if not url:
        return dict()
    r = requests.get(url)
    if r.status_code != 200:
        return HttpResponse("couldn't fetch it. sorry")

    if r.headers['content-type'].startswith('image/'):
        return dict(url=url)
    elif r.headers['content-type'].startswith('text/html'):
        tree = BeautifulSoup(r.text)
        images = [fix_base_path(i, url) for i in tree.findAll('img')
                  if get_width(i) > 75]
        image_links = [fix_link_base_path(i, url)
                       for i in tree.findAll('a')
                       if is_image_link(i)]
        return dict(html=True, images=images, links=image_links)
    else:
        return HttpResponse(
            "unknown content-type: %s" % r.headers['content-type'])


@transaction.non_atomic_requests
@rendered_with("main/import.html")
def import_url(request):
    if request.method == "GET":
        return import_url_form(request)
    if request.method == "POST":
        urls = []
        url = request.POST.get('url', '')
        if url != '':
            urls = [url]
        else:
            # probably an html page submission
            for k in request.POST.keys():
                if k.startswith("image_"):
                    url = k[len("image_"):]
                    urls.append(url)

        tags = parse_tags(request.POST.get('tags', ''))
        pairs = []
        try:
            for url in urls:
                image_id = models.create_image(url=url, tags=tags)
                pairs.append((image_id, url))
        except:
            raise
        else:
            for (image_id, url) in pairs:
                tasks.ingest_image.delay(image_id, url)
        return HttpResponseRedirect("/")
