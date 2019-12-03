from django.db import models
from accounts.models import UtentiRegistrati
from footballFieldManagement.models import CampiDaCalcio
from django.utils import timezone
import datetime


# Create your models here.

class payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    timestamp = models.DateField(auto_now_add=True)
    prezzo = models.FloatField()
    cliente = models.ForeignKey(UtentiRegistrati, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.cliente.username


class pendingReservation(models.Model):
    cliente = models.ForeignKey(UtentiRegistrati, on_delete=models.SET_NULL, blank=True, null=True)
    campo = models.ForeignKey(CampiDaCalcio, on_delete=models.CASCADE)
    data = models.DateField(default=timezone.now().date())
    ora = models.TimeField()
    accettato = models.BooleanField(default=None, null=True)
    payment = models.ForeignKey(payment, on_delete=models.SET_NULL, blank=True, null=True
                                )

    def __str__(self):
        return self.campo.nomeCampo + ' ' + self.data.strftime('%d/%m/%y') + ' ' + self.ora.strftime('%H:%M')

    class Meta:
        unique_together = (('campo', 'data', 'ora'),)
        verbose_name = 'Prenotazione in attesa'
        verbose_name_plural = 'Prenotazioni in attesa'

    def check_reservation_data(self):
        if self.data >= datetime.datetime.now().date():
            return True
        else:
            return False

    def check_reservation_data_hour(self):
        if self.data == datetime.datetime.now().date() and self.ora < datetime.datetime.now().time():
            print('True')
            return True
        else:
            return False


class review(models.Model):
    RATING_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    campo = models.ForeignKey(CampiDaCalcio, on_delete=models.CASCADE)
    utente = models.ForeignKey(UtentiRegistrati, on_delete=models.CASCADE)
    voto = models.IntegerField(choices=RATING_CHOICES)

    class Meta:
        unique_together = ['campo', 'utente']
        verbose_name = 'Recensione'
        verbose_name_plural = 'Recensioni'
