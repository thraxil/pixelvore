from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
import pixelvore.main.models as models
import pixelvore.main.tasks as tasks
from .utils import parse_tags
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse as urlparse
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random


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
    return render(request, "main/index.html",
                  dict(images=images, next_page_images=next_page_images))


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
    return render(request, "main/scroll.html",
                  dict(images=images, next_page_images=next_page_images))


def tag_index(request):
    return render(request, "main/tag_index.html",
                  dict(tags=models.get_all_tags()))


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
    return render(request, "main/tag.html", dict(images=images, tag=t))


def image(request, image_id):
    image = get_object_or_404(models.Image, id=image_id)
    return render(request, "main/image.html", dict(image=image))


def random_image(request):
    cnt = models.Image.objects.all().count()
    i = random.randint(0, cnt)
    image = models.Image.objects.all()[i]
    return render(request, "main/image.html", dict(image=image))


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
    if (not image['src'].startswith("http://")
            and not image['src'].startswith("https://")):
        image['src'] = urlparse.urljoin(base_url, image['src'])
    return image


def fix_link_base_path(link, base_url):
    if (not link['href'].startswith("http://")
            and not link['href'].startswith("https://")):
        link['href'] = urlparse.urljoin(base_url, link['href'])
    return link


def is_image_link(link):
    if not link.has_attr('href'):
        return False
    return link['href'].lower().endswith(".jpg") or \
        link['href'].lower().endswith(".jpeg") or \
        link['href'].lower().endswith(".png") or \
        link['href'].lower().endswith(".gif")


def import_url_form(request):
    url = request.GET.get('url', '')
    url = url.replace(" ", "%20").replace("+", "%20")
    if not url:
        return render(request, "main/import.html", dict())
    r = requests.get(url, verify=False)
    if r.status_code != 200:
        return HttpResponse("couldn't fetch it. sorry")

    if r.headers['content-type'].startswith('image/'):
        return render(request, "main/import.html", dict(url=url))
    elif r.headers['content-type'].startswith('text/html'):
        tree = BeautifulSoup(r.text)
        images = [{'src': fix_base_path(i, url)['src']}
                  for i in tree.findAll('img')
                  if get_width(i) > 75]
        image_links = [{'href': fix_link_base_path(i, url)['href']}
                       for i in tree.findAll('a')
                       if is_image_link(i)]
        return render(request, "main/import.html",
                      dict(html=True, images=images, links=image_links))
    else:
        return HttpResponse(
            "unknown content-type: %s" % r.headers['content-type'])


@transaction.non_atomic_requests
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
        except:  # noqa: E722
            raise
        else:
            for (image_id, url) in pairs:
                tasks.ingest_image.delay(image_id, url)
        return HttpResponseRedirect("/")
