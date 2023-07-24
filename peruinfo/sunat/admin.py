from django.contrib import admin

from .models import Padron



@admin.register(Padron)
class PadronAdmin(admin.ModelAdmin):
    pass