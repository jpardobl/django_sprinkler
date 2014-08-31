from django.conf.urls import patterns, include, url

urlpatterns = patterns('django_sprinkler',
    url(r"^get_context/?", "views.get_context", name="get_context"),
    url(r"^logs/?", "views.watering_logs", name="watering_logs"),
    url(r"^toggle_valve/(\d+)?/?", "views.toggle_valve", name="toggle_valve"),
    url(r"^activate_program/(\d+)?/?", "views.activate_program", name="activate_program"),
    url(r"^set_state/(\w+)?", "views.set_state", name="set_state"),
    url(r'^$', "views.home", name="home"),
    )