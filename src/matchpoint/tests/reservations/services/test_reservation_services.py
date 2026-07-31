from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from clubs.models import Club
from courts.models import Court
from openinghours.models import OpeningHours
from pricings.models import Prices
from datetime import datetime, time
from reservations.services import ReservationService

UserModel = get_user_model()


class TestReservations(APITestCase):
    def setUp(self) -> None:
        open = time(hour=8)
        close = time(hour=18)
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

    def test_get_total_price_for_reservation_returns_total_price(self):
        res = ReservationService.get_total_price_for_reservation(
            self.court,
            timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=9, minute=30))
            ),
            timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=10, minute=30))
            ),
        )
        self.assertEqual(res, 16.0)
