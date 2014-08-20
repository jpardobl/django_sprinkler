from django.core.management.base import BaseCommand, CommandError
from django_sprinkler.cicles import run
from datetime import datetime
import pytz
from django.conf import settings


class Command(BaseCommand):
    args = ''
    help = 'Evaluate rules realted to heater status. The result will start or stop the heater'

    def handle(self, *args, **options):
        self.stdout.write("Starting at %s" % datetime.now(pytz.timezone(settings.TIME_ZONE)))
        try:
            run()
        except Exception as ex2:
            self.stdout.write("Error ocurred: %s" % ex2)