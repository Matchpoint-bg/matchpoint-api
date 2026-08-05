from django.test import TestCase
from django.db.utils import IntegrityError, DataError
from django.core.exceptions import ValidationError
from clubs.factory import ClubFactory
from clubs.models import Club


class ClubModelTestCase(TestCase):
    def test_create_club_initiates_data(self):
        club = ClubFactory.create()
        self.assertEqual(club.name, "Test")
        self.assertEqual(club.city, "Sofia")

    def test_create_clubs_with_same_name_raises(self):
        club = ClubFactory.create()
        self.assertEqual(club.name, "Test")
        with self.assertRaises(IntegrityError):
            ClubFactory.create()

    def test_create_club_with_no_data_raises(self):
        club = ClubFactory.create()
        with self.assertRaises(ValidationError):
            club.full_clean()

    def test_create_club_with_long_name_raises(self):
        long_name = "a" * 101
        with self.assertRaises(DataError):
            Club.objects.create(name=long_name, latitude=10.0, longitude=10.0)
