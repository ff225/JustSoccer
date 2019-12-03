from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile, UtentiRegistrati, Proprietario
from django.core.validators import RegexValidator
from django.contrib.admin import widgets
import datetime


# date input field in forms template
class CustomDateInput(widgets.AdminTextInputWidget):
    input_type = 'date'


class RegUtente(UserCreationForm):
    numeric = RegexValidator(r'^[0-9]*$', 'Devono essere numeri!')
    ddn = forms.DateField(label='Data di nascita', widget=CustomDateInput)
    telefono = forms.CharField(required=True, max_length=10, label='Telefono', validators=[numeric])

    class Meta:
        model = UtentiRegistrati
        fields = ['username', 'email', 'first_name', 'last_name', 'ddn', 'citta']
        labels = {'first_name': _('Nome'), 'last_name': _('Cognome'), 'p_iva': _('Partita iva'), 'citta': _('Città'), }

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not UserProfile.objects.filter(telefono=telefono).exists() and telefono.isnumeric() and len(telefono) == 10:
            return telefono
        raise forms.ValidationError("Il numero di telefono è già stato utilizzato")

    def clean_ddn(self):
        ddn = self.cleaned_data['ddn']

        if ddn < datetime.date(1915, 1, 1) or ddn >= datetime.date.today():
            raise forms.ValidationError('Data di nascita non ammessa.')
        return ddn


class editUtente(UserChangeForm):
    numeric = RegexValidator(r'^[0-9]*$', 'Devono essere numeri!')
    telefono = forms.CharField(min_length=10, max_length=10, label='Telefono', validators=[numeric])
    ddn = forms.DateField(label='Data di nascita', widget=CustomDateInput)

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'ddn', 'citta', 'telefono']
        labels = {'first_name': _('Nome'), 'last_name': _('Cognome'), 'p_iva': _('Partita iva'), 'citta': _('Città'), }
        exclude = ('password', 'username')

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop('pk', None)
        super(editUtente, self).__init__(*args, **kwargs)

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if UserProfile.objects.filter(pk=self.pk, telefono=telefono).exists() and telefono.isnumeric() and len(
                telefono) == 10:
            return telefono
        elif not UserProfile.objects.filter(telefono=telefono).exists():
            return telefono
        else:
            raise forms.ValidationError("Il numero di telefono è già stato utilizzato")

    def clean_ddn(self):
        ddn = self.cleaned_data['ddn']

        if ddn < datetime.date(1915, 1, 1) or ddn > datetime.date.today():
            raise forms.ValidationError('Data di nascita non ammessa.')
        return ddn


class RegProprietario(UserCreationForm):
    numeric = RegexValidator(r'^[0-9]*$')
    telefono = forms.CharField(required=True, min_length=10, max_length=10, label='Telefono', validators=[numeric])
    ddn = forms.DateField(label='Data di nascita', widget=CustomDateInput)

    class Meta:
        model = Proprietario
        fields = ['username', 'email', 'first_name', 'last_name', 'ddn', 'p_iva', 'citta']
        labels = {'first_name': _('Nome'), 'last_name': _('Cognome'), 'p_iva': _('Partita iva'), 'citta': _('Città'), }
        # fields = ['username', 'email', 'nome', 'cognome', 'ddn', 'cap', 'telefono', 'p_iva']

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not UserProfile.objects.filter(telefono=telefono).exists() and telefono.isnumeric() and len(telefono) == 10:
            return telefono
        raise forms.ValidationError("Il numero di telefono è già stato utilizzato")

    def clean_p_iva(self):
        p_iva = self.cleaned_data['p_iva']
        if Proprietario.objects.filter(p_iva=p_iva).exists():
            raise forms.ValidationError('La partita iva esiste già')
        else:
            return p_iva

    def clean_ddn(self):
        ddn = self.cleaned_data['ddn']

        if ddn.year < datetime.date(1915, 1, 1).year or ddn >= datetime.date.today():
            raise forms.ValidationError('Data di nascita non ammessa.')
        elif (ddn.year + 18) > datetime.date.today().year:
            raise forms.ValidationError('Devi essere maggiorenne!')
        else:
            return ddn


class editProprietario(UserChangeForm):
    password = None
    numeric = RegexValidator(r'^[0-9]*$', 'Devono essere numeri!')
    telefono = forms.CharField(min_length=10, max_length=10, label='Telefono', validators=[numeric])
    p_iva = forms.CharField(max_length=11, min_length=11, label='Partita iva')

    class Meta:
        model = Proprietario
        fields = ['email', 'first_name', 'last_name', 'ddn', 'p_iva', 'citta']
        labels = {'first_name': _('Nome'), 'last_name': _('Cognome'), 'p_iva': _('Partita iva'), 'citta': _('Città'), }

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop('pk', None)
        super(editProprietario, self).__init__(*args, **kwargs)

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if UserProfile.objects.filter(pk=self.pk, telefono=telefono).exists() and telefono.isnumeric() and len(
                telefono) == 10:
            return telefono
        elif not UserProfile.objects.filter(telefono=telefono).exists():
            return telefono
        else:
            raise forms.ValidationError("Il numero di telefono è già stato utilizzato")

    def clean_ddn(self):
        ddn = self.cleaned_data['ddn']

        if ddn.year < datetime.date(1915, 1, 1).year or ddn >= datetime.date.today():
            raise forms.ValidationError('Data di nascita non ammessa.')
        elif (ddn.year + 18) > datetime.date.today().year:
            raise forms.ValidationError('Devi essere maggiorenne!')
        else:
            return ddn

    def clean_p_iva(self):
        p_iva = self.cleaned_data['p_iva']
        if Proprietario.objects.filter(pk=self.pk, p_iva=p_iva).exists() or not Proprietario.objects.filter(
                p_iva=p_iva).exists():
            return p_iva
        else:
            raise forms.ValidationError('La partita iva esiste già')
