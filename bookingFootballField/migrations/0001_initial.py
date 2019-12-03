# Generated by Django 2.2.6 on 2019-11-15 18:31

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('footballFieldManagement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_charge_id', models.CharField(max_length=50)),
                ('timestamp', models.DateField(auto_now_add=True)),
                ('prezzo', models.FloatField()),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.UtentiRegistrati')),
            ],
        ),
        migrations.CreateModel(
            name='review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voto', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('campo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='footballFieldManagement.CampiDaCalcio')),
                ('utente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.UtentiRegistrati')),
            ],
            options={
                'verbose_name': 'Recensione',
                'verbose_name_plural': 'Recensioni',
                'unique_together': {('campo', 'utente')},
            },
        ),
        migrations.CreateModel(
            name='pendingReservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=datetime.date(2019, 11, 15))),
                ('ora', models.TimeField()),
                ('accettato', models.BooleanField(default=None, null=True)),
                ('campo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='footballFieldManagement.CampiDaCalcio')),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.UtentiRegistrati')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bookingFootballField.payment')),
            ],
            options={
                'verbose_name': 'Prenotazione in attesa',
                'verbose_name_plural': 'Prenotazioni in attesa',
                'unique_together': {('campo', 'data', 'ora')},
            },
        ),
    ]
