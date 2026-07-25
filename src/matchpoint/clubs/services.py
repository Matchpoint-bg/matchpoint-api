import datetime
from django.utils import timezone

from common.exceptions import NoOpeningTimesFound
from common.helpers import get_weekday_name
from .models import Club
from openinghours.models import OpeningHours
from typing import Tuple


class ClubService:
    @staticmethod
    def get_opening_hours(
        club: Club, date: datetime.datetime
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        club_openings = OpeningHours.objects.filter(
            club=club, weekday=get_weekday_name(date)
        ).first()
        if not club_openings:
            raise NoOpeningTimesFound
        return timezone.make_aware(
            datetime.datetime.combine(date.date(), club_openings.opening_hour)
        ), timezone.make_aware(
            datetime.datetime.combine(date.date(), club_openings.closing_hour)
        )
