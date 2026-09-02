from django.contrib import admin
from .models import Court, CourtImages


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    pass


@admin.register(CourtImages)
class CourtImagesAdmin(admin.ModelAdmin):
    pass
