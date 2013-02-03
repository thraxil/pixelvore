from django.core.management.base import BaseCommand
import main.models
import main.tasks


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        for i in main.models.Image.objects.all():
            ext = i.thumb_set.all()[0].ext
            if ext != ".bmp":
                main.tasks.move_to_apomixis.delay(i.id, i.get_full_url(), ext)
