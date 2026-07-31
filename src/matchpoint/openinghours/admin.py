from django.contrib import admin
from django.contrib.admin import register

from openinghours.models import OpeningHours


@register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    pass
