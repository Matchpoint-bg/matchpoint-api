import datetime

from rest_framework.test import APITestCase
from common.helpers import (
    get_weekday_name,
    is_30_minutes,
    is_30_minutes_increment,
    is_minimum_30_minutes,
)


class TestCommonHelpers(APITestCase):
    def test_get_weekday_returns_weekday(self):
        weekday = get_weekday_name(datetime.datetime(year=2026, month=7, day=27))
        self.assertEqual(weekday, "Monday")

    def test_is_30_minute_increment_for_30_minutes_increments_returns_true(self):
        res = is_30_minutes_increment(datetime.time(hour=9, minute=0))
        self.assertTrue(res)

    def test_is_30_minute_increment_for_not_30_minutes_increments_returns_false(self):
        res = is_30_minutes_increment(datetime.time(hour=9, minute=10))
        self.assertFalse(res)

    def test_is_minimum_30_minutes_for_30_minutes_datetime_returns_true(self):
        date_start = datetime.datetime.combine(
            datetime.datetime.today(), datetime.time(hour=9)
        )
        date_end = datetime.datetime.combine(
            datetime.datetime.today(), datetime.time(hour=9, minute=30)
        )
        res = is_minimum_30_minutes(date_start, date_end)
        self.assertTrue(res)

    def test_is_minimum_30_minutes_for_30_minutes_time_returns_true(self):
        time_start = datetime.time(hour=9)
        time_end = datetime.time(hour=9, minute=30)
        res = is_minimum_30_minutes(time_start, time_end)
        self.assertTrue(res)

    def test_is_minimum_30_minutes_for_less_than_30_minutes_time_returns_false(self):
        time_start = datetime.time(hour=9)
        time_end = datetime.time(hour=9, minute=25)
        res = is_minimum_30_minutes(time_start, time_end)
        self.assertFalse(res)

    def test_is_30_minutes_for_30_minutes_datetime_returns_true(self):
        date_start = datetime.datetime.combine(
            datetime.datetime.today(), datetime.time(hour=9)
        )
        date_end = datetime.datetime.combine(
            datetime.datetime.today(), datetime.time(hour=9, minute=30)
        )
        res = is_30_minutes(date_start, date_end)
        self.assertTrue(res)

    def test_is_30_minutes_for_30_minutes_time_returns_true(self):
        date_start = datetime.time(hour=9)
        date_end = datetime.time(hour=9, minute=30)
        res = is_30_minutes(date_start, date_end)
        self.assertTrue(res)

    def test_is_30_minutes_for_less_than_30_minutes_time_returns_false(self):
        date_start = datetime.time(hour=9)
        date_end = datetime.time(hour=9, minute=28)
        res = is_30_minutes(date_start, date_end)
        self.assertFalse(res)

    def test_is_30_minutes_for_more_than_30_minutes_time_returns_false(self):
        date_start = datetime.time(hour=9)
        date_end = datetime.time(hour=9, minute=31)
        res = is_30_minutes(date_start, date_end)
        self.assertFalse(res)
