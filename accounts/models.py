from django.db import models
from django.contrib.auth.models import AbstractUser
from footballFieldManagement.models import CampiDaCalcio


# Create your models here.
class UserProfile(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    ddn = models.DateField(verbose_name='Data di nascita', default='1900-01-01')
    citta = models.CharField(max_length=100, default='')
    telefono = models.CharField(max_length=10, default='')


class UtentiRegistrati(UserProfile):

    class Meta:
        verbose_name_plural = 'Utenti registrati'

    def __str__(self):
        return self.email


class Proprietario(UserProfile):
    p_iva = models.CharField(max_length=11, null=False, unique=True)
    possiedeCampi = models.ManyToManyField(CampiDaCalcio, blank=True)

    class Meta:
        verbose_name_plural = 'Proprietari'

    def __str__(self):
        return self.email + ' ' + self.p_iva
