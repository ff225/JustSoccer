from django.db import models
from multiselectfield import MultiSelectField


# Create your models here.
class CampiDaCalcio(models.Model):
    GIORNI_APERTURA = (
        ('0', 'Lunedì'),
        ('1', 'Martedì'),
        ('2', 'Mercoledì'),
        ('3', 'Giovedì'),
        ('4', 'Venerdì'),
        ('5', 'Sabato'),
        ('6', 'Domenica'),
    )

    TIPO_CAMPO = (
        ('E', 'Erba sintetica'),
        ('T', 'Terra battuta'),
        ('P', 'Parquet'),
    )
    email = models.EmailField(max_length=255)
    nomeCampo = models.CharField(max_length=100)
    orario_apertura = models.TimeField(blank=False, default='00:00')
    orario_chiusura = models.TimeField(blank=False, default='00:00')
    via = models.CharField(max_length=100)
    civico = models.IntegerField()
    citta = models.CharField(max_length=100, default='')
    cap = models.CharField(max_length=5, default='')
    telefono = models.CharField(max_length=10)
    prezzo_campo = models.FloatField(verbose_name='prezzo campo/ora', default='50')
    giorni_apertura = MultiSelectField(choices=GIORNI_APERTURA, max_choices=7, blank=False)
    tipo_campo = MultiSelectField(choices=TIPO_CAMPO, max_choices=1, blank=False,
                                  error_messages={'errors': 'Impossibile selezionare più tipi'})
    longitudine = models.FloatField(default=50, blank=True)
    latitudine = models.FloatField(default=50, blank=True)
    image = models.ImageField(default='default.jpg', blank=True)
    chiuso = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.nomeCampo + ' ' + self.email + ', ' + self.via + ' ' + str(self.civico) + ', ' + self.citta

    class Meta:
        unique_together = ['via', 'civico', 'citta']
        verbose_name = 'Campo da calcio'
        verbose_name_plural = 'Campi da calcio'
        ordering = ['-nomeCampo', 'email', 'telefono']

    def check_orario_lavoro(self):
        if self.orario_apertura < self.orario_chiusura:
            return True
        else:
            return False

class eventi(models.Model):
    organizzatore = models.ForeignKey(CampiDaCalcio, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    descrizione = models.CharField(max_length=255)
    scadenza_iscrizione = models.DateField(default='1900-01-01')
    inizio_evento = models.DateField(default='1900-01-01')
    fine_evento = models.DateField(default='1900-01-01')
    foto_evento = models.ImageField(default='default.jpg', blank=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventi'

    def __str__(self):
        return self.titolo
