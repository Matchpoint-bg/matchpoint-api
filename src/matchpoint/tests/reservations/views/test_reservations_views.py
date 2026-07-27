from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from clubs.models import Club
from common.exceptions import IncorrectTimeException
from courts.models import Court
from openinghours.models import OpeningHours
from pricings.models import Prices
from datetime import datetime, time

from reservations.models import Reservation
from reservations.serializers import ReservationsSerializer
from reservations.services import ReservationService

UserModel = get_user_model()


class TestReservations(APITestCase):
    def setUp(self) -> None:
        open = time(hour=8)
        close = time(hour=18)
        self.user = UserModel.objects.create_user(
            email="<EMAIL>", password="<PASSWORD>"
        )
        self.club = Club.objects.create(name="Test")
        self.court = Court.objects.create(
            name="test", club_id=self.club, is_indoor=False, is_lit=False
        )
        for day in (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ):
            self.opening_hours = OpeningHours.objects.create(
                club=self.club,
                weekday=day,
                opening_hour=open,
                closing_hour=close,
            )

            # Create pricings for all the days of the week
            for x in range(open.hour, close.hour):
                Prices.objects.create(
                    court=self.court,
                    weekday=day,
                    time_start=time(hour=x),
                    time_end=time(hour=x, minute=30),
                    price_per_30_minutes=8,
                )
                Prices.objects.create(
                    court=self.court,
                    weekday=day,
                    time_start=time(hour=x, minute=30),
                    time_end=time(hour=x + 1),
                    price_per_30_minutes=8,
                )

        self.client = APIClient()

    def test_create_reservation_creates_reservation(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("reservation-list"),
            data={
                "court": self.court.pk,
                "user": self.user.pk,
                "start_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=10))
                ),
                "end_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=11))
                ),
            },
            format="json",
        )
        reservation = Reservation.objects.all().first()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reservation.user, self.user)

    def test_create_back_to_back_reservation_creates_reservations(self):
        self.client.force_authenticate(self.user)
        Reservation.objects.create(
            court=self.court,
            user=self.user,
            start_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=9))
            ),
            end_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=10))
            ),
        )
        resp = self.client.post(
            reverse("reservation-list"),
            data={
                "court": self.court.pk,
                "user": self.user.pk,
                "start_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=10))
                ),
                "end_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=11))
                ),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_reservation_with_incorrect_hour_raises(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("reservation-list"),
            data={
                "court": self.court.pk,
                "user": self.user.pk,
                "start_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=10, minute=15))
                ),
                "end_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=11))
                ),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_create_reservation_of_less_than_30_minutes_raises(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            reverse("reservation-list"),
            data={
                "court": self.court.pk,
                "user": self.user.pk,
                "start_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=10))
                ),
                "end_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=10, minute=15))
                ),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_create_reservation_while_busy_raises(self):
        self.client.force_authenticate(self.user)
        Reservation.objects.create(
            court=self.court,
            user=self.user,
            start_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=9))
            ),
            end_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=10))
            ),
        )
        resp = self.client.post(
            reverse("reservation-list"),
            data={
                "court": self.court.pk,
                "user": self.user.pk,
                "start_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=9, minute=30))
                ),
                "end_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=11))
                ),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data["message"],
            "Reservation impossible, the court is busy during this time",
        )
