from django.core.management.base import BaseCommand, CommandError
from django_sprinkler.cicles import run
from datetime import datetime
import pytz
from django.conf import settings

import logging

logger = logging.getLogger("watering")
logger.setLevel(settings.LOG_LEVEL)


class Command(BaseCommand):
    args = ''
    help = 'Evaluate rules realted to heater status. The result will start or stop the heater'

    def handle(self, *args, **options):
        now = datetime.now(pytz.timezone(settings.TIME_ZONE))
        self.stdout.write("Starting at %s" % now)
        logger.info("Starting cicle at %s" % now)
        try:
            run()
            logger.info("Ended cicle")
        except Exception as ex2:
            self.stdout.write("Error ocurred: %s" % ex2)
            logger.error(ex2)