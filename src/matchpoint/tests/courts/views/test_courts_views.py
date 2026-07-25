from rest_framework.test import APIClient, APITestCase
from courts.serializers import CourtSerializer
from django.utils import timezone
from django.contrib.auth import get_user_model
from courts.models import Court
from clubs.models import Club
from openinghours.models import OpeningHours
from pricings.models import Prices
from reservations.models import Reservation
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
import datetime

UserModel = get_user_model()
tz = timezone.get_current_timezone()


class TestCourtViewset(APITestCase):
    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            email="<EMAIL>", password="<PASSWORD>"
        )
        self.club = Club.objects.create(name="Test")
        self.court = Court.objects.create(
            name="test", club_id=self.club, is_indoor=False, is_lit=False
        )
        self.client = APIClient()

    def test_retrieve_court_retrieves_court(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("courts-detail", kwargs={"pk": self.court.pk}),
        )
        self.assertEqual(response.data, CourtSerializer(self.court).data)
        self.assertEqual(response.data["club_id"], self.club.pk)

    def test_retrieve_not_existing_court_returns_error(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("courts-detail", kwargs={"pk": "2"}),
        )
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data,
            {"status": "error", "message": "No Court matches the given query."},
        )

    def test_retrieve_court_schedule_returns_schedule(self):
        open = datetime.time(hour=8, minute=0)
        close = datetime.time(hour=17, minute=0)

        # Create a reservation object for the 2nd slot of the day

        reservation_start: datetime.datetime = timezone.make_aware(
            datetime.datetime.combine(timezone.now().date(), open)
            + datetime.timedelta(minutes=30),
            timezone=tz,
        )
        reservation_end: datetime.datetime = timezone.make_aware(
            datetime.datetime.combine(timezone.now().date(), open)
            + datetime.timedelta(hours=1, minutes=30),
            timezone=tz,
        )

        Reservation.objects.create(
            court=self.court,
            user_id=self.user.pk,
            start_datetime=reservation_start,
            end_datetime=reservation_end,
        )

        # Set up opening hours for all the days of the week

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
                    time_start=datetime.time(hour=x),
                    time_end=datetime.time(hour=open.hour, minute=30),
                    price_per_30_minutes=8,
                )
                Prices.objects.create(
                    court=self.court,
                    weekday=day,
                    time_start=datetime.time(hour=x, minute=31),
                    time_end=datetime.time(hour=open.hour + 1),
                    price_per_30_minutes=8,
                )

        # Authenticate

        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("courts-schedule", kwargs={"pk": self.court.pk}),
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

        # Check that 1st slot is available

        self.assertEqual(
            response.data[0]["start"],
            timezone.make_aware(
                datetime.datetime.combine(timezone.now(), open)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.assertEqual(
            response.data[0]["end"],
            timezone.make_aware(
                datetime.datetime.combine(timezone.now(), open)
                + datetime.timedelta(minutes=30)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.assertTrue(response.data[0]["available"])
        self.assertEqual(response.data[0]["price"], 8)

        # Check that second slot is not available
        self.assertEqual(
            response.data[1]["start"],
            timezone.make_aware(
                datetime.datetime.combine(timezone.now(), open)
                + datetime.timedelta(minutes=30)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.assertEqual(
            response.data[1]["end"],
            timezone.make_aware(
                datetime.datetime.combine(timezone.now(), open)
                + datetime.timedelta(minutes=60)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.assertFalse(response.data[1]["available"])
        self.assertEqual(response.data[1]["price"], 0)
