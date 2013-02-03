from django.core.management.base import BaseCommand
from main.models import dump_everything


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        print dump_everything()
