from django import forms
import datetime
from footballFieldManagement.forms import CustomDateInput, CustomTimeInput


class SearchPitch(forms.Form):
    TIPO_CAMPO = (
        ('E', 'Erba sintetica'),
        ('T', 'Terra battuta'),
        ('P', 'Parquet'),
    )
    citta = forms.CharField(max_length=100, required=True)
    prezzo_campo = forms.FloatField(widget=forms.NumberInput, required=True)
    orario_apertura = forms.TimeField(label='A che ora vuoi giocare?', required=True, widget=CustomTimeInput)
    giorni_apertura = forms.DateField(label='Inserisci data', widget=CustomDateInput, required=True)
    tipo_campo = forms.MultipleChoiceField(choices=TIPO_CAMPO, required=True)

    def clean_orario_apertura(self):
        orario_apertura = self.cleaned_data['orario_apertura']
        print(type(orario_apertura))
        orario_apertura = datetime.time(orario_apertura.hour, 00)

        return orario_apertura

    def clean_giorni_apertura(self):
        giorni_apertura = self.cleaned_data['giorni_apertura']

        if giorni_apertura < datetime.datetime.today().date():
            raise forms.ValidationError('La data non è valida')

        return giorni_apertura

    def clean(self):
        cleaned_data = super().clean()
        orario_apertura = cleaned_data.get('orario_apertura')
        giorno = cleaned_data.get('giorni_apertura')

        if giorno == datetime.date.today() and orario_apertura.hour <= datetime.datetime.now().time().hour:
            return self.add_error('orario_apertura', 'Orario non consentito.')


class SearchBase(forms.Form):
    citta = forms.CharField(max_length=100, required=True)
    orario_apertura = forms.TimeField(label='A che ora vuoi giocare?', required=True, widget=CustomTimeInput)
    giorni_apertura = forms.DateField(label='Inserisci data', widget=CustomDateInput, required=True)

    def clean_giorni_apertura(self):
        giorni_apertura = self.cleaned_data['giorni_apertura']

        if giorni_apertura < datetime.datetime.today().date():
            raise forms.ValidationError('La data non è valida')

        return giorni_apertura

    def clean_orario_apertura(self):
        orario_apertura = self.cleaned_data['orario_apertura']
        print(type(orario_apertura))
        orario_apertura = datetime.time(orario_apertura.hour, 00)
        return orario_apertura

    def clean(self):
        cleaned_data = super().clean()
        orario_apertura = cleaned_data.get('orario_apertura')
        giorno = cleaned_data.get('giorni_apertura')

        if giorno == datetime.date.today() and orario_apertura.hour <= datetime.datetime.now().time().hour:
            return self.add_error('orario_apertura', 'Orario non consentito.')
