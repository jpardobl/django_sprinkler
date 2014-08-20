from django.contrib import admin
from django_sprinkler.models import *


class SprinklerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Sprinkler, SprinklerAdmin)


class ProgramAdmin(admin.ModelAdmin):
    pass
admin.site.register(Program, ProgramAdmin)


class ProgramStepAdmin(admin.ModelAdmin):
    pass
admin.site.register(ProgramStep, ProgramStepAdmin)


class ContextAdmin(admin.ModelAdmin):
    pass
admin.site.register(Context, ContextAdmin)


class StartTimeAdmin(admin.ModelAdmin):
    pass
admin.site.register(StartTime, StartTimeAdmin)