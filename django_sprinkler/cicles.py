from django_sprinkler.models import Program, Context


def run():
    ctxt = Context.objects.get_context()
    #check state

    program = ctxt.active_program

    if ctxt.state in ('automatic', 'running_program'):
        pass
    if ctxt.state == '3min_cicle':
        pass
    if ctxt.state == 'cicle':
        pass





