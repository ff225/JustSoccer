from django.contrib import admin
from footballFieldManagement.models import *


# Register your models here.
class CampiDaCalcioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nomeCampo', 'citta', 'chiuso',)
    list_filter = ('citta', 'chiuso')
    ordering = ('citta',)


class eventiAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'organizzatore')
    list_filter = ('organizzatore',)


admin.site.register(CampiDaCalcio, CampiDaCalcioAdmin)
admin.site.register(eventi, eventiAdmin)
