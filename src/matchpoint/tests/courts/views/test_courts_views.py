from rest_framework.test import APIClient, APITestCase
from clubs.factory import ClubFactory
from courts.serializers import CourtSerializer
from django.utils import timezone
from django.contrib.auth import get_user_model
from courts.models import Court
from clubs.models import Club
from openinghours.models import OpeningHours
from pricings.models import Prices
from reservations.models import Reservation
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
import datetime

UserModel = get_user_model()
tz = timezone.get_current_timezone()


class TestCourtViewset(APITestCase):
    def create_schedule(self):
        open = datetime.time(hour=8, minute=0)
        close = datetime.time(hour=17, minute=0)
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

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user(
            email="<EMAIL>", password="<PASSWORD>"
        )
        self.club = ClubFactory.create()
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
        self.create_schedule()

        # Authenticate

        self.client.force_authenticate(self.user)
        url = reverse("courts-court-availabilities", kwargs={"pk": self.court.pk})
        response = self.client.get(url, {"date": datetime.datetime.today().date()})
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

    def test_get_court_prices_returns_prices(self):

        self.club.employees.add(self.user)

        self.create_schedule()
        # Authenticate

        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("courts-prices", kwargs={"pk": self.court.pk})
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_court_prices_unauthorized_user_returns_403(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("courts-prices", kwargs={"pk": self.court.pk})
        )
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_put_court_prices_creates_prices(self):
        self.create_schedule()
        self.club.employees.add(self.user)
        self.client.force_authenticate(self.user)
        url = reverse("courts-prices", kwargs={"pk": self.court.pk})
        response = self.client.put(
            url,
            data=[
                {
                    "weekday": "Sunday",
                    "time_start": "08:00",
                    "time_end": "08:30",
                    "price_per_30_minutes": 4,
                }
            ],
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        prices = Prices.objects.all()
        self.assertEqual(prices.count(), 1)

    def test_availabilities_endpoints_create_and_returns_unavailabilities(self):
        self.create_schedule()
        self.club.employees.add(self.user)
        self.client.force_authenticate(self.user)

        url = reverse("courts-unavailabilities", kwargs={"pk": self.court.pk})

        resp = self.client.put(
            url,
            data={
                "start_datetime": datetime.datetime(year=2026, day=2, month=8, hour=9),
                "end_datetime": datetime.datetime(year=2026, day=2, month=8, hour=17),
            },
        )

        self.assertEqual(resp.status_code, HTTP_201_CREATED)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(
            resp.data[0],
            {
                "pk": 1,
                "start_datetime": "2026-08-02T09:00:00Z",
                "end_datetime": "2026-08-02T17:00:00Z",
            },
        )
