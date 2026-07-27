import datetime

from django.utils import timezone


def get_weekday_name(date: datetime.date):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return days[date.weekday()]


def is_30_minutes_increment(date: datetime.datetime | datetime.time):
    return date.minute in (0, 30) and date.second == 0 and date.microsecond == 0


def is_minimum_30_minutes(
    start_time: datetime.datetime | datetime.time,
    end_time: datetime.datetime | datetime.time,
):
    if isinstance(start_time, datetime.time):
        start_time = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.today(), start_time)
        )
    if isinstance(end_time, datetime.time):
        end_time = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.today(), end_time)
        )
    return end_time - start_time >= datetime.timedelta(minutes=30)


def is_30_minutes(
    start_time: datetime.datetime | datetime.time,
    end_time: datetime.datetime | datetime.time,
):
    if isinstance(start_time, datetime.time):
        start_time = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.today(), start_time)
        )
    if isinstance(end_time, datetime.time):
        end_time = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.today(), end_time)
        )
    return end_time - start_time == datetime.timedelta(minutes=30)
