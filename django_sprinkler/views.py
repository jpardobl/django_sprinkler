from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django_sprinkler.models import Context, Sprinkler, Program
from django.http import HttpResponse, HttpResponseServerError
from django_sprinkler.settings import *
import logging, simplejson
from django.conf import settings
from django_sprinkler.cicles import run


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

logger_watering = logging.getLogger("watering")
logger_watering.setLevel(logger.level)


def watering_logs(request):
    #print settings.LOGGING["handlers"]["watering"]
    f = open(settings.LOGGING["handlers"]["watering"]["filename"], "r")

    lines = []
    for line in f.readlines():
        lines.append(line.split(";;", line.count(";;")))

    return render_to_response(
        "sprinkler/log.html",
        {"log": lines}
    )



def get_context(request):
    ctxt = Context.objects.get_context()

    response = HttpResponse(
        content=ctxt.to_json(),
        content_type="application/json")
    response['Cache-Control'] = 'no-cache'
    return response


def toggle_valve(request, valve_id):

    sprinkler = get_object_or_404(Sprinkler, id=valve_id)
    try:
        sprinkler.toggle()
        return get_context(request)
    except Exception as ex:
        logger.error("Error at toggle_valve: %s" % ex)
        return HttpResponseServerError(ex)


def activate_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    try:
        ctxt = Context.objects.get_or_create(state='manual')[0]
        ctxt.active_program = program
        ctxt.save()
        logger_watering.info("Changing active program to: %s" % program)
        return get_context(request)
    except Exception as et:
        logger.error("Error at activate_program: %s" % et)
        return HttpResponseServerError(et)


def set_state(request, new_state):
    try:
        #print "new_state: %s" % new_state
        ctxt = Context.objects.get_context()
        if new_state in ("3min_cicle", "cicle"):
           run()
        ctxt.state = new_state
        if new_state == "manual":
            ctxt.start_at = None
        ctxt.save()

        #resetamos todos los riegos
        [s.toggle(False) for s in Sprinkler.objects.all()]
        logger_watering.info("Changing state to %s" % ctxt.state)
        return get_context(request)
    except Exception as et:
        logger.error("Error at set_state: %s" % et)
        return HttpResponseServerError(et)


def home(request):
    return render_to_response(
        "sprinkler/home.html",
        {}
    )