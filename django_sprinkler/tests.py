import unittest, simplejson, logging, pytz
from django_sprinkler.models import *
from hautomation_restclient.manage import *
from django_sprinkler.settings import *
from django.conf import settings
from django.utils.timezone import utc


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestSprinklers(unittest.TestCase):

    def _now(self):
        return datetime.now(pytz.timezone(settings.TIME_ZONE))

    def _create_sprinklers(self):
        [x.delete() for x in Sprinkler.objects.all()]

        Sprinkler(caption="aspe1", did=1).save()
        Sprinkler(caption="aspe2", did=2).save()
        Sprinkler(caption="aspe3", did=3).save()

    def _create_program(self):
        [x.delete() for x in ProgramStep.objects.all()]
        [x.delete() for x in Program.objects.all()]
        p = Program()
        p.save()

        stp1 = ProgramStep(
            sprinkler=Sprinkler.objects.get(caption="aspe1"),
            minutes=10,
            order=1)
        stp1.save()

        p.steps.add(stp1)

        stp2 = ProgramStep(
            sprinkler=Sprinkler.objects.get(caption="aspe2"),
            minutes=10,
            order=2)
        stp2.save()

        p.steps.add(stp2)

        stp3 = ProgramStep(
            sprinkler=Sprinkler.objects.get(caption="aspe3"),
            minutes=10,
            order=3)
        stp3.save()
        p.steps.add(stp3)

    def test_program_active_step_minutes(self):
        self._create_sprinklers()
        self._create_program()

        logger.debug("******************* NO DAY ***********************")

        logger.debug("#################################### Must find None: start now + 10min")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.save()

        p.starting_times.add(st)

        ret = p.has_active_step(minutes=3)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is 10 min later: %s" % ret)

        st.time = self._now() - timedelta(minutes=2)
        logger.debug("#################################### Must find aspe1: start -2min")
        st.save()
        ret = p.has_active_step(minutes=3)
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe1").sprinkler.caption, ret.sprinkler.caption,
            "Not properly calculating active step.\
           Should return stp1 as start time is 2 min ago and stp1 is 3min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=4)
        logger.debug("#################################### Must find aspe2: start -4min")
        st.save()

        ret = p.has_active_step(minutes=3)
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe2").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp2 as start time is 4 min ago and stp2\
            is 3min long + stp1 3min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=7)
        logger.debug("#################################### Must find aspe3: start -25min")
        st.save()

        ret = p.has_active_step(minutes=3)
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe3").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp3 as start time is 7 min \
           ago and stp3 is 3min long + stp2 3min long + stp1 3min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=2)
        logger.debug("#################################### Must find aspe1: start -9min")
        st.save()

        ret = p.has_active_step(minutes=3)
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe1").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp1 as start time is 2 \
           min ago and stp1 is 3min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=4)
        logger.debug("#################################### Must find aspe2: start -11min")
        st.save()

        ret = p.has_active_step(minutes=3)
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe2").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp2 as start time is 4 min\
            ago and stp1 is 3min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: start -60min")
        st.save()

        ret = p.has_active_step(minutes=3)
        self.assertIsNone(ret,
           "Not properly calculating active step.\
           Should return None as start time is 60 min\
            and program only lasts for 30min")

    def test_program_active_step_one_hour_ago(self):
        self._create_sprinklers()
        self._create_program()

        startt = self._now()-timedelta(hours=1)

        logger.debug("******************* NO DAY ***********************")

        logger.debug("#################################### Must find None: start now + 10min")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.save()

        p.starting_times.add(st)

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour ago: %s" % ret)

        st.time = self._now() - timedelta(minutes=2)
        logger.debug("#################################### Must find aspe1: start -2min")
        st.save()
        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour ago: %s" % ret)

        st.time = self._now() - timedelta(minutes=4)
        logger.debug("#################################### Must find aspe2: start -4min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour ago: %s" % ret)

        st.time = self._now() - timedelta(minutes=7)
        logger.debug("#################################### Must find aspe3: start -25min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour ago: %s" % ret)

        st.time = self._now() - timedelta(minutes=2)
        logger.debug("#################################### Must find aspe1: start -9min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour ago: %s" % ret)

        st.time = self._now() - timedelta(minutes=4)
        logger.debug("#################################### Must find aspe2: start -11min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour ago: %s" % ret)

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: start -60min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour ago: %s" % ret)

    def test_program_active_step_one_hour_later(self):
        self._create_sprinklers()
        self._create_program()

        startt = self._now()+timedelta(hours=1)

        logger.debug("******************* NO DAY ***********************")

        logger.debug("#################################### Must find None: start now + 10min")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.save()

        p.starting_times.add(st)

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour later: %s" % ret)

        st.time = self._now() - timedelta(minutes=2)
        logger.debug("#################################### Must find aspe1: start -2min")
        st.save()
        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour later: %s" % ret)

        st.time = self._now() - timedelta(minutes=4)
        logger.debug("#################################### Must find aspe2: start -4min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour later: %s" % ret)

        st.time = self._now() - timedelta(minutes=7)
        logger.debug("#################################### Must find aspe3: start -25min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour later: %s" % ret)

        st.time = self._now() - timedelta(minutes=2)
        logger.debug("#################################### Must find aspe1: start -9min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour later: %s" % ret)

        st.time = self._now() - timedelta(minutes=4)
        logger.debug("#################################### Must find aspe2: start -11min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour later: %s" % ret)

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: start -60min")
        st.save()

        ret = p.has_active_step(program_must_start_at=startt)
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is one hour later: %s" % ret)


    def test_program_active_step_without_days(self):
        self._create_sprinklers()
        self._create_program()

        logger.debug("******************* NO DAY ***********************")

        logger.debug("#################################### Must find None: start now + 10min")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.save()

        p.starting_times.add(st)

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is 10 min later: %s" % ret)

        st.time = self._now() - timedelta(minutes=5)
        logger.debug("#################################### Must find aspe1: start -5min")
        st.save()
        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe1").sprinkler.caption, ret.sprinkler.caption,
            "Not properly calculating active step.\
           Should return stp1 as start time is 5 min ago and stp1 is 10min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=15)
        logger.debug("#################################### Must find aspe2: start -15min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe2").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp2 as start time is 15 min ago and stp2\
            is 10min long + stp1 10min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=25)
        logger.debug("#################################### Must find aspe3: start -25min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe3").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp3 as start time is 25 min \
           ago and stp3 is 10min long + stp2 10min long + stp1 10min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=9)
        logger.debug("#################################### Must find aspe1: start -9min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe1").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp1 as start time is 9 \
           min ago and stp1 is 10min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=11)
        logger.debug("#################################### Must find aspe2: start -11min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe2").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp2 as start time is 11 min\
            ago and stp1 is 10min long: %s" % ret)

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: start -60min")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(ret,
           "Not properly calculating active step.\
           Should return None as start time is 60 min\
            and program only lasts for 30min")

    def test_program_active_step_today(self):
        self._create_sprinklers()
        self._create_program()
        now = self._now()

        logger.debug("******************************* TODAY ***********************")
        p = Program.objects.get()

        st = StartTime(time=now + timedelta(minutes=10))
        st.week_day = now.strftime("%a")
        st.save()

        p.starting_times.add(st)
        logger.debug("#################################### Must find None: start +10min")
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as the starting time of the program\
            is 10 min later: %s" % ret)

        st.time = now - timedelta(minutes=5)
        logger.debug("#################################### Must find aspe1: start -5min")
        st.save()
        ret = p.has_active_step()
        self.assertEqual("aspe1", ret.sprinkler.caption,
            "Not properly calculating active step.\
           Should return stp1 as start time is 5 min ago and stp1 is 10min long: %s" % ret)

        st.time = now - timedelta(minutes=15)
        logger.debug("#################################### Must find aspe2: start -15min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe2").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp2 as start time is 15 min ago and stp2\
            is 10min long + stp1 10min long: %s" % ret)

        st.time = now - timedelta(minutes=25)
        logger.debug("#################################### Must find aspe3: start -25min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe3").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp3 as start time is 25 min \
           ago and stp3 is 10min long + stp2 10min long + stp1 10min long: %s" % ret)

        st.time = now - timedelta(minutes=9)
        logger.debug("#################################### Must find aspe1: start -9min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe1").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp1 as start time is 9 \
           min ago and stp1 is 10min long: %s" % ret)

        st.time = now - timedelta(minutes=11)
        logger.debug("#################################### Must find aspe2: start -11min")
        st.save()

        ret = p.has_active_step()
        self.assertEqual(ProgramStep.objects.get(sprinkler__caption="aspe2").sprinkler.caption, ret.sprinkler.caption,
           "Not properly calculating active step.\
           Should return stp2 as start time is 11 min\
            ago and stp1 is 10min long: %s" % ret)

        st.time = now - timedelta(hours=1)
        logger.debug("#################################### Must find None: start -60min")
        st.save()

        ret = p.has_active_step()
        logger.debug("start: %s ------------------ ret: %s" % (st.time, ret))
        self.assertIsNone(ret,
           "Not properly calculating active step.\
           Should return None as start time is 60 min\
            and program only lasts for 30min")

    def test_program_active_step_tomorrow(self):
        self._create_sprinklers()
        self._create_program()
        logger.debug("******************* TOMORROW ***********************")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.week_day = (self._now() + timedelta(days=1)).strftime("%a")
        st.save()

        p.starting_times.add(st)
        logger.debug("#################################### Must find None: No day matching")
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is tomorrow")

        st.time = self._now() - timedelta(minutes=5)
        logger.debug("#################################### Must find None: No day matching")
        st.save()
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is tomorrow")

        st.time = self._now() - timedelta(minutes=15)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is tomorrow")

        st.time = self._now() - timedelta(minutes=25)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is tomorrow")

        st.time = self._now() - timedelta(minutes=9)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is tomorrow")

        st.time = self._now() - timedelta(minutes=11)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is tomorrow")

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is tomorrow")


    def test_program_active_step_yesterday(self):
        self._create_sprinklers()
        self._create_program()
        logger.debug("******************* YESTERDAY ***********************")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.week_day = (self._now() - timedelta(days=1)).strftime("%a")
        st.save()

        p.starting_times.add(st)
        logger.debug("#################################### Must find None: No day matching")
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=5)
        logger.debug("#################################### Must find None: No day matching")
        st.save()
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=15)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=25)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=9)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=11)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

    def test_program_active_step_yesterday_and_tomorrow(self):
        self._create_sprinklers()
        self._create_program()
        logger.debug("******************* YESTERDAY & TOMORROW ***********************")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.week_day = "%s,%s" % (
            (self._now() - timedelta(days=1)).strftime("%a"),
            (self._now() + timedelta(days=1)).strftime("%a"))
        st.save()

        p.starting_times.add(st)
        logger.debug("#################################### Must find None: No day matching")
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=5)
        logger.debug("#################################### Must find None: No day matching")
        st.save()
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=15)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=25)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=9)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=11)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.week_day = " %s , %s " % (
            (self._now() - timedelta(days=1)).strftime("%a"),
            (self._now() + timedelta(days=1)).strftime("%a"),)
        st.save()

        p.starting_times.add(st)
        logger.debug("#################################### Must find None: No day matching")
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=5)
        logger.debug("#################################### Must find None: No day matching")
        st.save()
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=15)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=25)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=9)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=11)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: No day matching")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None active step as days is yesterday")

    def test_program_active_step_today_and_tomorrow(self):
        self._create_sprinklers()
        self._create_program()
        logger.debug("******************* TODAY & TOMORROW ***********************")
        p = Program.objects.get()

        st = StartTime(time=self._now() + timedelta(minutes=10))
        st.week_day = "%s,%s" % (
            self._now().strftime("%a"),
            (self._now() + timedelta(days=1)).strftime("%a"))
        st.save()

        p.starting_times.add(st)
        logger.debug("#################################### Must find None: start +10min")
        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None as program starts in 10min")

        st.time = self._now() - timedelta(minutes=5)
        logger.debug("#################################### Must find aspe1: start -5min")
        st.save()
        ret = p.has_active_step()
        self.assertEquals(
            ProgramStep.objects.get(sprinkler__caption="aspe1"),
            ret,
            "Not properly calculating active step.\
            Should return stp1 as program has started 5min before")

        st.time = self._now() - timedelta(minutes=15)
        logger.debug("#################################### Must find aspe2: start -15min")
        st.save()

        ret = p.has_active_step()
        self.assertEquals(
            ProgramStep.objects.get(sprinkler__caption="aspe2"),
            ret,
            "Not properly calculating active step.\
            Should return stp2 as program has started 15min before")

        st.time = self._now() - timedelta(minutes=25)
        logger.debug("#################################### Must find aspe3: start -25min")
        st.save()

        ret = p.has_active_step()
        self.assertEquals(
            ProgramStep.objects.get(sprinkler__caption="aspe3"),
            ret,
            "Not properly calculating active step.\
            Should return stp3 as program has started 25min before")

        st.time = self._now() - timedelta(minutes=9)
        logger.debug("#################################### Must find aspe1: start -9min")
        st.save()

        ret = p.has_active_step()
        self.assertEquals(
            ProgramStep.objects.get(sprinkler__caption="aspe1"),
            ret,
            "Not properly calculating active step.\
            Should return stp1 as program has started 9min before")

        st.time = self._now() - timedelta(minutes=11)
        logger.debug("#################################### Must find aspe2: start -11min")
        st.save()

        ret = p.has_active_step()
        self.assertEquals(
            ProgramStep.objects.get(sprinkler__caption="aspe2"),
            ret,
            "Not properly calculating active step.\
            Should return stp2 as program has started 11min before")

        st.time = self._now() - timedelta(minutes=60)
        logger.debug("#################################### Must find None: stat -60min")
        st.save()

        ret = p.has_active_step()
        self.assertIsNone(
            ret,
            "Not properly calculating active step.\
            Should return None as program is started 60min ago and only lasts for 30min")

    def test_manage_sprinkler(self):
        [x.delete() for x in Sprinkler.objects.all()]
        Sprinkler(caption="cesped", did=1).save()

        s = Sprinkler.objects.get()
        self.assertIsInstance(s, Sprinkler)

        self.assertDictEqual(
            {
            "caption": "cesped",
            "did": 1,
            "status": False,
            "device_type": "switch",
            "protocol": "GPIO",
            },
            get_device("GPIO",
                       1,
                       API_HOST,
                       API_USERNAME,
                       API_PASSWORD)[0]
        )
        s.delete()

        self.assertTrue(
            len(get_device("GPIO",
               1,
               API_HOST,
               API_USERNAME,
               API_PASSWORD)) == 0,
            "Not properly deleting sprinkler")





  #TODO rest of the tests



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGPIO)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    unittest.main()