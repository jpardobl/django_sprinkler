from django_sprinkler.models import Program, Context
from datetime import datetime
import pytz, logging
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

logger_watering = logging.getLogger("watering")
logger_watering.setLevel(logger.level)


def exec_step(ctxt, step=None):
    if ctxt.state == "manual":
        logger.info("State is manual, thus not acting")
        return

    for pstep in ctxt.active_program.steps.all():
        if step == pstep:
            #Arrancamos el aspersor que ha sido devuelto como activo
            pstep.sprinkler.toggle(True)
            continue
        #apagamos el resto de aspersores
        pstep.sprinkler.toggle(False)


def run():

    ctxt = Context.objects.get_context()
    program = ctxt.active_program

    #check state
    try:
        if ctxt.state == 'manual':
            next_step = None

        elif ctxt.state in ('automatic', 'running_program'):
            next_step = program.has_active_step()

        elif ctxt.state == '3min_cicle':
            startt = datetime.now(pytz.timezone(settings.TIME_ZONE)) \
                if ctxt.start_at is None \
                else ctxt.start_at
            next_step = program.has_active_step(program_must_start_at=startt, minutes=3)

        elif ctxt.state == 'cicle':
            startt = datetime.now(pytz.timezone(settings.TIME_ZONE)) \
                if ctxt.start_at is None \
                else ctxt.start_at
            next_step = program.has_active_step(program_must_start_at=startt)

        exec_step(ctxt, next_step)
    except Program.ProgramMustJumpException as ex:
        return

