from django import forms
from .models import pendingReservation, review


class pendingReservationForm(forms.ModelForm):
    class Meta:
        model = pendingReservation
        fields = '__all__'
        exclude = ('accettato', 'payment')


class confirmReservation(forms.ModelForm):
    class Meta:
        model = pendingReservation
        fields = ('accettato',)
        exclude = '__all__'


class reviewForm(forms.ModelForm):
    class Meta:
        model = review
        fields = '__all__'
