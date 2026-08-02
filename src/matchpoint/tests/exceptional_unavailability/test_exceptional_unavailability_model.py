from datetime import datetime, time
from django.db import IntegrityError
from rest_framework.test import APITestCase
from common.exceptions import IncorrectTimeException
from courts.models import Court
from clubs.models import Club
from exceptionalunavailability.models import ExceptionalUnavailability


class TestExceptionalUnavailabilityModel(APITestCase):
    def setUp(self) -> None:
        self.club = Club.objects.create(name="Test")
        self.court = Court.objects.create(
            name="test", club_id=self.club, is_indoor=False, is_lit=False
        )

    def test_create_exceptional_unavailability_creates_object(self):
        unavailability = ExceptionalUnavailability(
            club=self.club,
            court=self.court,
            start_datetime=datetime.combine(datetime.today(), time(hour=10, minute=30)),
            end_datetime=datetime.combine(datetime.today(), time(hour=11)),
        )
        unavailability.full_clean()
        unavailability.save()
        self.assertEqual(ExceptionalUnavailability.objects.count(), 1)

    def test_create_exceptional_unavailability_incorrect_time_raises(self):
        unavailability = ExceptionalUnavailability(
            club=self.club,
            court=self.court,
            start_datetime=datetime.combine(datetime.today(), time(hour=10, minute=15)),
            end_datetime=datetime.combine(datetime.today(), time(hour=11)),
        )
        with self.assertRaises(IncorrectTimeException):
            unavailability.full_clean()

    def test_create_two_unavailabilities_for_same_court_and_date_raises(self):
        ExceptionalUnavailability.objects.create(
            club=self.club,
            court=self.court,
            start_datetime=datetime.combine(datetime.today(), time(hour=10, minute=30)),
            end_datetime=datetime.combine(datetime.today(), time(hour=11)),
        )
        with self.assertRaises(IntegrityError):
            ExceptionalUnavailability.objects.create(
                club=self.club,
                court=self.court,
                start_datetime=datetime.combine(
                    datetime.today(), time(hour=10, minute=30)
                ),
                end_datetime=datetime.combine(datetime.today(), time(hour=11)),
            )
