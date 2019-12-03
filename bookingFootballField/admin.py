from django.contrib import admin
from bookingFootballField.models import *


# Register your models here.
class pendingReservationAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'campo', 'data', 'ora', 'accettato')
    list_filter = ('data', 'ora')
    search_fields = ('cliente__first_name', 'campo__nomeCampo')
    ordering = ('data', 'ora',)


class reviewAdmin(admin.ModelAdmin):
    list_display = ('campo', 'utente', 'voto')
    ordering = ('campo',)


class paymentAdmin(admin.ModelAdmin):
    list_display = ('stripe_charge_id', 'cliente',)


admin.site.register(pendingReservation, pendingReservationAdmin)
admin.site.register(review, reviewAdmin)
admin.site.register(payment, paymentAdmin)
