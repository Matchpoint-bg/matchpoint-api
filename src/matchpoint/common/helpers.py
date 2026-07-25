import datetime


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
