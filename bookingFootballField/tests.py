from django.test import TestCase
from .models import pendingReservation
import datetime


# Create your tests here.

class ReservationTestCast(TestCase):

    def test_reservation_now(self):
        data = datetime.datetime.today().date()
        reservation = pendingReservation(data=data, ora='21:00:00', accettato=None,
                                         campo_id=1, cliente_id=3, payment_id=None)

        self.assertEqual(reservation.check_reservation_data(), True)

    def test_reservation_future(self):
        data = datetime.datetime.today().date() + datetime.timedelta(days=5)
        reservation = pendingReservation(data=data, ora='21:00:00', accettato=None,
                                         campo_id=1, cliente_id=3, payment_id=None)

        self.assertEqual(reservation.check_reservation_data(), True)

    def test_reservation_past(self):
        data = datetime.datetime.today().date() - datetime.timedelta(days=5)
        reservation = pendingReservation(data=data, ora='21:00:00', accettato=None,
                                         campo_id=1, cliente_id=3, payment_id=None)

        self.assertEqual(reservation.check_reservation_data(), False)

    def test_reservation_date_hour_correct(self):
        data = datetime.datetime.today().date()
        ora = datetime.datetime.strptime('21:00:00', '%H:%M:%S').time()
        reservation = pendingReservation(data=data, ora=ora, accettato=None,
                                         campo_id=1, cliente_id=3, payment_id=None)

        self.assertEqual(reservation.check_reservation_data_hour(), False)

    def test_reservation_date_hour_wrong(self):
        data = datetime.datetime.today().date()
        time = datetime.datetime.now().time()
        hour = time.hour - 1
        time = time.replace(hour=hour, minute=00)
        reservation = pendingReservation(data=data, ora=time, accettato=None,
                                         campo_id=1, cliente_id=3, payment_id=None)

        self.assertEqual(reservation.check_reservation_data_hour(), True)
