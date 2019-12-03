from django import forms
from django.utils.translation import gettext_lazy as _
from footballFieldManagement.models import CampiDaCalcio, eventi
from django.core.validators import RegexValidator
from django.contrib.admin import widgets
import datetime
from geopy.geocoders import Here
from PrenotazioneCampi.settings import MAPS_APP_CODE, MAPS_API_ID


class CustomDateInput(widgets.AdminTextInputWidget):
    input_type = 'date'


class CustomTimeInput(widgets.AdminTextInputWidget):
    input_type = 'time'
    format = '%H'


class AddFootballField(forms.ModelForm):
    numeric = RegexValidator(r'^[0-9]*$', 'Devono essere numeri!')
    cap = forms.CharField(min_length=5, max_length=5, validators=[numeric])
    prezzo_campo = forms.FloatField(widget=forms.NumberInput)
    orario_apertura = orario_chiusura = forms.TimeField(widget=CustomTimeInput)

    class Meta:
        model = CampiDaCalcio
        fields = '__all__'
        labels = {'nomeCampo': _('Nome campo'), 'citta': _('Città')}

    def clean_orario_apertura(self):
        orario_apertura = self.cleaned_data['orario_apertura']
        print(type(orario_apertura))
        orario_apertura = datetime.time(orario_apertura.hour, 00)

        return orario_apertura

    def clean_orario_chiusura(self):
        orario_chiusura = self.cleaned_data['orario_chiusura']
        orario_chiusura = datetime.time(orario_chiusura.hour, 00)

        return orario_chiusura

    def clean_citta(self):
        maps = Here(app_id=MAPS_API_ID, app_code=MAPS_APP_CODE)
        citta = self.cleaned_data['citta']
        ck_citta = maps.geocode(citta)

        ck_citta = str(ck_citta).split(', ')

        if ck_citta[0] == 'None':
            raise forms.ValidationError('Indirizzo errato')
        else:
            return citta.upper()


class CreateEvent(forms.ModelForm):
    organizzatore = forms.CheckboxInput()
    scadenza_iscrizione = forms.DateField(label='Scadenza iscrizione', widget=CustomDateInput)
    descrizione = forms.CharField(widget=forms.Textarea())
    inizio_evento = forms.DateField(label='Inizio evento', widget=CustomDateInput)
    fine_evento = forms.DateField(label='Fine evento', widget=CustomDateInput)

    class Meta:
        model = eventi
        fields = '__all__'

    def clean_scadenza_iscrizione(self):
        scadenza_iscrizione = self.cleaned_data['scadenza_iscrizione']

        if scadenza_iscrizione < datetime.datetime.today().date():
            raise forms.ValidationError('La data non è valida')
        else:
            return scadenza_iscrizione

    def clean_inizio_evento(self):
        inizio_evento = self.cleaned_data['inizio_evento']

        if inizio_evento < datetime.datetime.today().date():
            raise forms.ValidationError('La data non è valida')
        else:
            return inizio_evento

    def clean_fine_evento(self):
        fine_evento = self.cleaned_data['fine_evento']

        if fine_evento < datetime.datetime.today().date():
            raise forms.ValidationError('La data non è valida')
        else:
            return fine_evento

    def clean(self):
        cleaned_data = super().clean()

        scadenza_iscrizione = cleaned_data.get("scadenza_iscrizione")
        inizio_evento = cleaned_data.get("inizio_evento")
        fine_evento = cleaned_data.get("fine_evento")

        if scadenza_iscrizione != None:
            if scadenza_iscrizione > inizio_evento:
                return self.add_error('scadenza_iscrizione', 'La data di scadenza non ammissibile')
        elif inizio_evento > fine_evento:

            return self.add_error('inizio_evento', 'Le date di inizio e fine evento non sono ammissibili')
