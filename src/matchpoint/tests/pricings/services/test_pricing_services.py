import datetime
from rest_framework.test import APITestCase
from clubs.factory import ClubFactory
from clubs.models import Club
from courts.models import Court
from pricings.models import Prices
from pricings.services import PricingService


class TestPricingServices(APITestCase):
    def setUp(self) -> None:
        self.club = ClubFactory.create()
        self.court = Court.objects.create(
            name="test", club_id=self.club, is_indoor=False, is_lit=False
        )
        self.prices = Prices.objects.create(
            court=self.court,
            weekday="Friday",
            time_start=datetime.time(hour=8),
            time_end=datetime.time(hour=9),
            price_per_30_minutes=4,
        )

    def test_calculate_amount_per_period_returns_amount(self):
        amt = PricingService().calculate_amount_for_period(
            datetime.time(hour=8), datetime.time(hour=9), 8
        )
        self.assertEqual(amt, 16)

    def test_get_pricing_for_30_minutes_returns_price(self):
        amt = PricingService().get_price_for_30_minutes(
            weekday="Friday",
            time_start=datetime.time(hour=8),
            time_end=datetime.time(hour=8, minute=30),
            court=self.court,
        )
        self.assertEqual(amt, 4)

    def test_get_pricing_for_30_minutes_no_data_raises(self):
        with self.assertRaises(Exception) as e:
            PricingService().get_price_for_30_minutes(
                weekday="Friday",
                time_start=datetime.time(hour=8),
                time_end=datetime.time(hour=9, minute=30),
                court=self.court,
            )
            self.assertEqual(e.msg, "No price found for this data")
