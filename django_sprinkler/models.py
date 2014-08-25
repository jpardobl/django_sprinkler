from django.db import models
import simplejson, logging, pytz
from hautomation_restclient.cmds import *
from hautomation_restclient.manage import *
from django_sprinkler.settings import *
from django.core.exceptions import MultipleObjectsReturned
from datetime import datetime, timedelta, tzinfo
from django.conf import settings
from time import strptime, strftime, mktime
from django.utils import timezone


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

logger_watering = logging.getLogger("watering")
logger_watering.setLevel(logger.level)


STATE_CHOICES = (
    ('automatic', 'Automatic'),
    ('manual', 'Manual'),
    ('3min_cicle', 'Running 3min cicle'),
    ('cicle', 'Running cicle'),
    ('running_program', 'Running program'),
)


class ContextManager(models.Manager):
    @staticmethod
    def get_context():
        try:
            return Context.objects.get()
        except Context.DoesNotExist:
            c = Context()
            c.save()
            return c
        except MultipleObjectsReturned:
            [c.delete() for c in Context.objects.all()]
            return Context.objects.get_context()


class StartTime(models.Model):
    time = models.TimeField()
    week_day = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return u"Every %s at %s" %(
            self.week_day if not self.week_day in (None, "") else "day",
            self.time,
        )


class Context(models.Model):
    objects = ContextManager()
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default='manual')
    active_program = models.ForeignKey("Program", null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    simulation = models.BooleanField(default=True)

    def to_json(self):
        if self.active_program is None:
            valves = [[s.to_dict(), None] for s in Sprinkler.objects.all()]
        else:
            valves = [[s.sprinkler.to_dict(), s.minutes] for s in self.active_program.steps.all()]


        return simplejson.dumps({
            "time": datetime.now(pytz.timezone(settings.TIME_ZONE)).strftime("%H:%M"),
            "state": self.state,
            "active_program": self.active_program.id if self.active_program is not None else None,
            "valves": valves,
            "simulation": self.simulation,
            "programs": [p.to_dict() for p in Program.objects.all()],
        })


class Sprinkler(models.Model):
    did = models.IntegerField()
    caption = models.CharField(max_length=100)
    state = models.BooleanField(default=False)
    api_host = models.CharField(max_length=200, default=API_HOST)


    def __unicode__(self):
        return u"%s - %s" % (self.did, self.caption)

    def to_dict(self):
        return {
            "id": self.id,
            "did": self.did,
            "caption": self.caption,
            "state": self.state,
        }

    def save(self):
        try:

            if self.pk is None and not Context.objects.get_context().simulation:
                add_device(
                    "GPIO",
                    self.did,
                    "sprinkler_%s" % self.did,
                    "switch",
                    self.api_host,
                    API_USERNAME,
                    API_PASSWORD)

        except RestApiException as er:
            logger.debug("Error creating sprinkler into API server, %s" % er)
        super(Sprinkler, self).save()

    def delete(self):
        try:
            if not Context.objects.get_context().simulation:
                del_device(
                    "GPIO",
                    self.did,
                    self.api_host,
                    API_USERNAME,
                    API_PASSWORD)

        except RestApiException as er:
            logger.debug("Error deleting sprinkler into API server, %s" % er)
        super(Sprinkler, self).delete()

    def toggle(self, new_state=None):
        sim = Context.objects.get_context().simulation
        if new_state is None:
            self.state = not self.state
        else:
            if self.state == new_state:
                logger_watering.info("Sprinkler %s already at state: %s" % (self, self.state))
                return

            self.state = new_state
        self.save()
        if not sim:
            pl_switch("GPIO",
                self.did,
                "on" if self.state else "off",
                self.api_host,
                API_USERNAME,
                API_PASSWORD)

        logger_watering.info("Sprinkler %s now at state: %s (simulation: %s)" % (self, self.state, sim))


class ProgramStep(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    sprinkler = models.ForeignKey(Sprinkler)
    minutes = models.IntegerField(default=5)
    order = models.IntegerField()

    class Meta:
        ordering = ["order", ]

    def __unicode__(self):
        return u"%s %s %s" %(
            self.sprinkler,
            self.minutes,
            self.order
        )

class Program(models.Model):
    name = models.CharField(max_length=20, blank=True)
    steps = models.ManyToManyField(ProgramStep, null=True, blank=True)
    starting_times = models.ManyToManyField(StartTime)

    def save(self):

        try:
            if self.name is None:
                self.name = "Program"
                override = True

            super(Program, self).save()
            if override:
                self.name = "%s %s" % (self.name, self.id)
                super(Program, self).save()
        except UnboundLocalError as ule:
            pass

    def __unicode__(self):
        sts = u"%s" % self.name
        for x in self.starting_times.all():
            sts = u"%s; %s" % (sts, x)
        return sts

    def to_dict(self):
        return {
            "id": self.id,
            "name": u"%s" % self,
        }

    def has_active_step(self, program_must_start_at=None, minutes=None):
        now = datetime.now(pytz.timezone(settings.TIME_ZONE))
        if program_must_start_at is None:
            #Use program starting time to check active steps
            for start in self.starting_times.all():
                start.time = start.time.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
                logger_watering.debug("promgram promgramed start: %s" % start.time)
                #Is program supposed to be run today?
                if not start.week_day in (None, ""):
                    logger_watering.debug("Weekday not is None")
                    days = [x.strip() for x in start.week_day.split(",")]
                    logger_watering.debug("Days: %s, %s" % (days, now.strftime("%a")))
                    if len(days) and not now.strftime("%a") in days:
                        logger.debug("No watering for today")
                        continue
               # program_start = now
               # logger.debug("program_start: %s" % program_start)
                program_start = now.replace(hour=start.time.hour).replace(minute=start.time.minute).replace(second=0)

           #     logger.debug("program_start: %s" % program_start)
            #    program_start += timedelta(hours=start.time.hour, minutes=start.time.minute)
           #     logger.debug("program_start: %s after adding: %s hours" % (program_start, start.time.hour))
           #     program_start += timedelta(minutes=start.time.minute)
                logger_watering.debug("program_start: %s" % program_start)

                return self.active_step(
                    program_start,
                    minutes)
        else:
            #Use passed program_start to calculate active_steps
            return self.active_step(program_must_start_at, minutes)
        logging.debug("NO STEP FOUND")
        return None

    def active_step(self, program_start, minutes):


        c = Context.objects.get_context()

        now = datetime.now(pytz.timezone(settings.TIME_ZONE))

        #length of time adding the duration of each step
        length = 0
        for step in self.steps.all():
            logger_watering.debug("Working with step: %s" % step)
            #Use minutes passed if not None, else we use program minutes
            length += step.minutes if minutes is None else minutes
            step_end = program_start + timedelta(minutes=length)
           # logger.info("%s - %s - %s" % (timezone.is_naive(program_start), timezone.is_naive(now), timezone.is_naive(step_end)))
            logger_watering.debug("%s < %s < %s" % (program_start, now, step_end))
            #logger.info("%s < %s < %s ???" % (program_start.tzinfo, now.tzinfo, step_end.tzinfo))

            if settings.DEBUG:
                if program_start < now:
                    logger_watering.debug("program_start < now")
                if now < step_end:
                    logger_watering.debug("now < step_end")

            if program_start < now < step_end:
                #if Context.program_start is None means this is the first
                #step of the program, need to initialize the program_start time
                if c.start_at is None:
                    c.start_at = program_start
                    if c.state == "automatic":
                        logger_watering.info("Changing state Automatic -> running_program")
                        c.state = "running_program"
                    c.save()
                logger_watering.debug("FOUND: %s (type: %s)" % (step, type(step)))
                return step
        #unset the Context.program_start as the program has no step left

        c.start_at = None
        c.save()
        logger_watering.debug("NO STEP FOUND")
        return None



