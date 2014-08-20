from django.core.management.base import BaseCommand, CommandError
from time import localtime, strftime, sleep


class Command(BaseCommand):
    args = ''
    help = 'Evaluate rules realted to heater status. The result will start or stop the heater'

    def handle(self, *args, **options):
        self.stdout.write("Starting at %s" % strftime("%d.%m.%Y %H:%M:%S", localtime()))
        try:
            evaluate_non_themp()
        except Exception as ex2:
            self.sdout.write("Error ocurred: %s" % ex2)