import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from clubs.factory import ClubFactory
from openinghours.models import OpeningHours
from clubs.services import ClubService

UserModel = get_user_model()


class TestClubsAPIViews(APITestCase):
    def setUp(self) -> None:
        self.user = UserModel.objects.create_superuser(
            email="<EMAIL>", password="<PASSWORD>"
        )
        self.club = ClubFactory.create()

    def test_retrieve_opening_hours_returns_opening_hours(self):
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
                opening_hour=datetime.time(hour=8, minute=0),
                closing_hour=datetime.time(hour=17, minute=0),
            )

        self.opening_hours.refresh_from_db()
        hours = ClubService.get_opening_hours(
            club=self.club, date=datetime.datetime.now()
        )
        self.assertEqual(
            (
                timezone.make_aware(
                    datetime.datetime.combine(
                        datetime.datetime.now().date(), datetime.time(hour=8, minute=0)
                    )
                ),
                timezone.make_aware(
                    datetime.datetime.combine(
                        datetime.datetime.now().date(), datetime.time(hour=17, minute=0)
                    )
                ),
            ),
            hours,
        )

    def test_retrieve_opening_hours_not_set_raises(self):
        with self.assertRaises(Exception):
            ClubService.get_opening_hours(
                club=self.club, date=datetime.datetime(year=2026, month=7, day=17)
            )
