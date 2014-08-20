from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django_sprinkler.models import Context, Sprinkler, Program
from django.http import HttpResponse, HttpResponseServerError
from django_sprinkler.settings import *
import logging


logger = logging.getLogger("views")
logger.setLevel(LOG_LEVEL)


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
        return get_context(request)
    except Exception as et:
        logger.error("Error at activate_program: %s" % et)
        return HttpResponseServerError(et)


def set_state(request, new_state):
    try:
        #print "new_state: %s" % new_state
        ctxt = Context.objects.get_context()
        if new_state in ("3min_cicle", "cicle"):
            pass
            #TODO activate manual cicle
        ctxt.state = new_state
        ctxt.save()

        #resetamos todos los riegos
        [s.toggle(False) for s in Sprinkler.objects.all()]

        return get_context(request)
    except Exception as et:
        logger.error("Error at set_state: %s" % et)
        return HttpResponseServerError(et)


def home(request):
    return render_to_response(
        "sprinkler/home.html",
        {}
    )