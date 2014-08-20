from django_sprinkler.models import Program, Context
from datetime import datetime
import pytz, logging
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)


def exec_step(ctxt, step=None):
    if step is None:
        #No hay mas pasos en el programa,
        #si venimos de running_program lo dejamos como automatic
        #si venimos de otro estado, volvemos a manual
        ctxt.state = 'automatic' if ctxt.state == 'running_program' else 'manual'
        ctxt.save()

    for pstep in ctxt.active_program.steps.all():

        if step == pstep:
            #Arrancamos el aspersor que ha sido devuelto como activo
            pstep.sprinkler.toggle(True)
            continue
        #apagamos el resto de aspersores
        pstep.sprinkler.toggle(False)


def run():
    ctxt = Context.objects.get_context()
    #check state

    if ctxt.state == 'manual':
        logger.info("State is Manual, thus not acting")
        return exec_step(ctxt, None)

    program = ctxt.active_program

    if ctxt.state in ('automatic', 'running_program'):
        return exec_step(ctxt, program.has_active_step())
    if ctxt.state == '3min_cicle':
        return exec_step(ctxt, program.has_active_step(
            program_must_start_at=datetime.now(pytz.timezone(settings.TIME_ZONE)),
            minutes=3))
    if ctxt.state == 'cicle':
        return exec_step(ctxt, program.has_active_step(
            program_must_start_at=datetime.now(pytz.timezone(settings.TIME_ZONE))))







