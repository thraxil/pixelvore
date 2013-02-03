from django.core.management.base import BaseCommand
from main.models import delete_everything


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        delete_everything()
