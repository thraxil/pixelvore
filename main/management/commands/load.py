from django.core.management.base import BaseCommand
from main.models import *

class Command(BaseCommand):
    args = ''
    help = ''
    
    def handle(self, *args, **options):
        load_everything("dump.json")
