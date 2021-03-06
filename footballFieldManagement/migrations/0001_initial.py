# Generated by Django 2.2.6 on 2019-11-15 18:31

from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CampiDaCalcio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255)),
                ('nomeCampo', models.CharField(max_length=100)),
                ('orario_apertura', models.TimeField(default='00:00')),
                ('orario_chiusura', models.TimeField(default='00:00')),
                ('via', models.CharField(max_length=100)),
                ('civico', models.IntegerField()),
                ('citta', models.CharField(default='', max_length=100)),
                ('cap', models.CharField(default='', max_length=5)),
                ('telefono', models.CharField(max_length=10)),
                ('prezzo_campo', models.FloatField(default='50', verbose_name='prezzo campo/ora')),
                ('giorni_apertura', multiselectfield.db.fields.MultiSelectField(choices=[('0', 'Lunedì'), ('1', 'Martedì'), ('2', 'Mercoledì'), ('3', 'Giovedì'), ('4', 'Venerdì'), ('5', 'Sabato'), ('6', 'Domenica')], max_length=13)),
                ('tipo_campo', multiselectfield.db.fields.MultiSelectField(choices=[('E', 'Erba sintetica'), ('T', 'Terra battuta'), ('P', 'Parquet')], error_messages={'errors': 'Impossibile selezionare più tipi'}, max_length=5)),
                ('longitudine', models.FloatField(blank=True, default=50)),
                ('latitudine', models.FloatField(blank=True, default=50)),
                ('image', models.ImageField(blank=True, default='default.jpg', upload_to='')),
                ('chiuso', models.BooleanField(blank=True, default=False, null=True)),
            ],
            options={
                'verbose_name': 'Campo da calcio',
                'verbose_name_plural': 'Campi da calcio',
                'ordering': ['-nomeCampo', 'email', 'telefono'],
                'unique_together': {('via', 'civico', 'citta')},
            },
        ),
        migrations.CreateModel(
            name='eventi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titolo', models.CharField(max_length=100)),
                ('descrizione', models.CharField(max_length=255)),
                ('scadenza_iscrizione', models.DateField(default='1900-01-01')),
                ('inizio_evento', models.DateField(default='1900-01-01')),
                ('fine_evento', models.DateField(default='1900-01-01')),
                ('foto_evento', models.ImageField(blank=True, default='default.jpg', upload_to='')),
                ('organizzatore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='footballFieldManagement.CampiDaCalcio')),
            ],
            options={
                'verbose_name': 'Evento',
                'verbose_name_plural': 'Eventi',
            },
        ),
    ]
