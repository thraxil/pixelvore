from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
import models
import tasks
from utils import parse_tags

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

def index(request):
    return HttpResponse("here")

def import_url(request):
    if request.method == "GET":
        url = request.GET.get('url','')
        # TODO: instead of just displaying it,
        # we ought to fetch and check the content-type
        # and display form to pick images if it's html
        return HttpResponse("""
<html>
<body>
<form action="." method="post">
<input type="hidden" name="url" value="%s" />
<input type="submit" value="ingest"/>
</form>
<img src="%s" />
</body>
</html>
""" % (url,url))
    if request.method == "POST":
        url = request.POST.get('url','')
        if url == '':
            return HttpResponse("no url")
        slug = models.create_image(url=url)
        tasks.ingest_image.delay(slug,url)
        return HttpResponseRedirect("/")
