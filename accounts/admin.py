from django.contrib import admin
from accounts.models import *
from .forms import RegProprietario, RegUtente


# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'ddn',)
    list_display_links = ('email',)
    ordering = ('first_name', 'last_name',)


class UtentiRegistratiAdmin(admin.ModelAdmin):
    search_fields = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'ddn',)
    list_display_links = ('email',)
    ordering = ('first_name', 'last_name',)
    form = RegUtente


class ProprietarioAdmin(admin.ModelAdmin):
    search_fields = ('email',)
    list_display = ('email', 'p_iva', 'first_name', 'last_name',)
    list_display_links = ('email',)
    ordering = ['p_iva', ]
    form = RegProprietario


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UtentiRegistrati, UtentiRegistratiAdmin)
admin.site.register(Proprietario, ProprietarioAdmin)
