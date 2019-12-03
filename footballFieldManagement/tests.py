from django.test import TestCase
from .models import CampiDaCalcio
import datetime


# Create your tests here.

class footballFieldTest(TestCase):

    def test_orario_lavoro_correct(self):
        stop = datetime.datetime.now().time()
        hour = stop.hour - 1
        start = stop.replace(hour=hour, minute=00)
        campo = CampiDaCalcio(email='asd@jp.com', nomeCampo='test', orario_apertura=start, orario_chiusura=stop,
                              giorni_apertura=('0', '1', '2', '3', '4', '5', '6'))

        self.assertEqual(campo.check_orario_lavoro(), True)

    def test_orario_lavoro_equal(self):
        start = stop = datetime.datetime.now().time()

        campo = CampiDaCalcio(email='asd@jp.com', nomeCampo='test', orario_apertura=start, orario_chiusura=stop,
                              giorni_apertura=('0', '1', '2', '3', '4', '5', '6'))

        self.assertEqual(campo.check_orario_lavoro(), False)

    def test_orario_lavoro_wrong(self):
        stop = datetime.datetime.now().time()
        hour = stop.hour - 1
        start = stop.replace(hour=hour, minute=00)

        campo = CampiDaCalcio(email='asd@jp.com', nomeCampo='test', orario_apertura=stop, orario_chiusura=start,
                              giorni_apertura=('0', '1', '2', '3', '4', '5', '6'))

        self.assertEqual(campo.check_orario_lavoro(), False)
