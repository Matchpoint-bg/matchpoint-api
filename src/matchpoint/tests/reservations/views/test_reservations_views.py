from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from clubs.factory import ClubFactory
from clubs.models import Club
from courts.models import Court
from openinghours.models import OpeningHours
from pricings.models import Prices
from datetime import datetime, time

from reservations.models import Reservation

UserModel = get_user_model()


class TestReservations(APITestCase):
    def setUp(self) -> None:
        open = time(hour=8)
        close = time(hour=18)
        self.user = UserModel.objects.create_user(
            email="<EMAIL>", password="<PASSWORD>"
        )
        self.club = ClubFactory.create()
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

    def test_create_reservation_with_incorrect_start_hour_raises(self):
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

    def test_create_reservation_with_incorrect_end_hour_raises(self):
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
                    datetime.combine(datetime.today(), time(hour=11, minute=15))
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
        self.assertEqual(
            resp.content,
            b'{"status":"error","message":"The time is not a 30 minutes increment"}',
        )
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

    def test_list_reservations_for_normal_user_returns_user_reservation(self):
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
        resp = self.client.get(reverse("reservation-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        user = UserModel.objects.create(email="<EMAIL2>", password="<PASSOWRD")
        self.client.force_authenticate(user)
        resp = self.client.get(reverse("reservation-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)

    def test_list_reservations_for_staff_user_returns_all_reservation(self):
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
        user = UserModel.objects.create(
            email="<EMAIL2>", password="<PASSOWRD", is_staff=True
        )
        self.client.force_authenticate(user)
        resp = self.client.get(reverse("reservation-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_get_reservations_for_normal_user_returns_user_reservation(self):
        self.client.force_authenticate(self.user)
        res = Reservation.objects.create(
            court=self.court,
            user=self.user,
            start_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=9))
            ),
            end_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=10))
            ),
        )
        resp = self.client.get(reverse("reservation-detail", kwargs={"pk": res.pk}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["user"], self.user.pk)
        user = UserModel.objects.create(email="<EMAIL2>", password="<PASSOWRD")
        self.client.force_authenticate(user)
        resp = self.client.get(reverse("reservation-detail", kwargs={"pk": res.pk}))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_reservation_updates_reservation(self):
        self.client.force_authenticate(self.user)
        res = Reservation.objects.create(
            court=self.court,
            user=self.user,
            start_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=9))
            ),
            end_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=10))
            ),
        )
        resp = self.client.put(
            reverse("reservation-detail", kwargs={"pk": res.pk}),
            data={
                "court": res.court.pk,
                "start_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=9))
                ),
                "end_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=11))
                ),
            },
            format="json",
        )
        print(resp.content)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        res.refresh_from_db()
        self.assertEqual(
            res.end_datetime,
            timezone.make_aware(datetime.combine(datetime.today(), time(hour=11))),
        )

    def test_update_reservation_with_incorrect_time_returns_400(self):
        self.client.force_authenticate(self.user)
        res = Reservation.objects.create(
            court=self.court,
            user=self.user,
            start_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=9))
            ),
            end_datetime=timezone.make_aware(
                datetime.combine(datetime.today(), time(hour=10))
            ),
        )
        resp = self.client.put(
            reverse("reservation-detail", kwargs={"pk": res.pk}),
            data={
                "court": self.court.pk,
                "start_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=9, minute=15))
                ),
                "end_datetime": timezone.make_aware(
                    datetime.combine(datetime.today(), time(hour=11))
                ),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.content,
            b'{"status":"error","message":"The time is not a 30 minutes increment"}',
        )
        res.refresh_from_db()
        self.assertEqual(
            res.start_datetime,
            timezone.make_aware(datetime.combine(datetime.today(), time(hour=9))),
        )
