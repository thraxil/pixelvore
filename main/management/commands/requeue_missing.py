from django.core.management.base import BaseCommand
import main.models
import main.tasks

class Command(BaseCommand):
    args = ''
    help = ''
    
    def handle(self, *args, **options):
        for i in main.models.Image.objects.all():
            st = i.get_stream_url()
            tt = i.get_squarethumb_url()
            ft = i.get_full_url()
            if None in [st,tt,ft]:
                print "redoing %s" % i.url
                # clear it out
                for t in i.thumb_set.all():
                    t.delete()
                main.tasks.ingest_image.delay(i.id,i.url)
