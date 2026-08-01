# Register your models here.
from django.contrib import admin
from django.contrib.admin import register

from pricings.models import Prices


@register(Prices)
class PricesAdmin(admin.ModelAdmin):
    pass
