import datetime
from django.db.models.query import QuerySet
from django.utils import timezone

from common.exceptions import NoOpeningTimesFound
from common.helpers import get_weekday_name, haversine
from .models import Club
from openinghours.models import OpeningHours
from typing import Tuple


class ClubService:
    @staticmethod
    def get_opening_hours(
        club: Club, date: datetime.datetime | datetime.date
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        club_openings = OpeningHours.objects.filter(
            club=club, weekday=get_weekday_name(date)
        ).first()
        if not club_openings:
            raise NoOpeningTimesFound
        if isinstance(date, datetime.datetime):
            return timezone.make_aware(
                datetime.datetime.combine(date.date(), club_openings.opening_hour)
            ), timezone.make_aware(
                datetime.datetime.combine(date.date(), club_openings.closing_hour)
            )
        else:
            return timezone.make_aware(
                datetime.datetime.combine(date, club_openings.opening_hour)
            ), timezone.make_aware(
                datetime.datetime.combine(date, club_openings.closing_hour)
            )

    @staticmethod
    def fiter_by_distance(
        queryset: QuerySet, lat: float, long: float, radius: float = 10
    ):
        clubs = Club.objects.exclude(latitude=None).exclude(longitude=None)

        for club in clubs:
            dist = haversine(club.latitude, club.longitude, lat, long)
            if dist > radius:
                queryset.objects.exclude(club)

        return queryset
