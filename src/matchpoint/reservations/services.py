from typing import Tuple, List
from clubs.services import ClubService
from common.exceptions import CourtBusyException, IncorrectTimeException
from common.helpers import get_weekday_name, is_minimum_30_minutes
from courts.models import Court
from pricings.services import PricingService
from users.models import CustomUser
from .models import Reservation
from exceptionalunavailability.models import ExceptionalUnavailability
from django.db import transaction
import datetime
from django.db.models import Q


class ReservationService:
    @staticmethod
    def is_available(
        court: Court,
        start: datetime.datetime,
        end: datetime.datetime,
        current_res_id: int | None = None,
    ) -> bool:
        existing_reservations = (
            Reservation.objects.filter(
                Q(court=court) & (Q(start_datetime__lt=end) & Q(end_datetime__gt=start))
            )
            .exclude(pk=current_res_id)
            .exists()
        )
        exceptional_closures = ExceptionalUnavailability.objects.filter(
            court=court, start_datetime__lt=end, end_datetime__gt=start
        )
        return not existing_reservations and not exceptional_closures

    @staticmethod
    def _get_unavailable_times(
        court: Court, date: datetime.datetime
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        day, month, year = date.day, date.month, date.year
        unavailable_times = []
        reserved_times = Reservation.objects.filter(
            court=court,
            start_datetime__gt=datetime.datetime(
                year=year, month=month, day=day, hour=0, minute=0, second=0
            ),
            end_datetime__lt=datetime.datetime(
                year=year, month=month, day=day, hour=23, minute=59, second=59
            ),
        )
        unavailable_times.extend(
            [
                (reservation.start_datetime, reservation.end_datetime)
                for reservation in reserved_times
            ]
        )
        closing_times = ExceptionalUnavailability.objects.filter(
            court=court,
            start_datetime__gt=datetime.datetime(
                year=year, month=month, day=day, hour=0, minute=0, second=0
            ),
            end_datetime__lt=datetime.datetime(
                year=year, month=month, day=day, hour=23, minute=59, second=59
            ),
        )
        unavailable_times.extend(
            [
                (closing_time.start_datetime, closing_time.end_datetime)
                for closing_time in closing_times
            ]
        )
        return unavailable_times

    @staticmethod
    def _is_slot_available(
        start: datetime.datetime,
        end: datetime.datetime,
        unavailabilities: List[Tuple[datetime.datetime, datetime.datetime]],
    ):
        for unavailable_start, unavailable_end in unavailabilities:
            if unavailable_start < end and unavailable_end > start:
                return False
        return True

    @staticmethod
    def get_availability(court: Court, date: datetime.datetime) -> List[dict]:
        unavailable_times = ReservationService._get_unavailable_times(court, date)
        opening, closing = ClubService.get_opening_hours(court.club_id, date)
        slots = []
        slot: datetime.datetime = opening
        while slot < closing:
            next_slot = slot + datetime.timedelta(minutes=30)
            slots.append(
                {
                    "start": slot,
                    "end": next_slot,
                    "available": ReservationService._is_slot_available(
                        slot, next_slot, unavailable_times
                    ),
                    "price": ReservationService._get_price_for_slot(
                        court, slot, next_slot
                    ),
                }
            )
            slot = next_slot
        return slots

    @staticmethod
    def _get_price_for_slot(
        court: Court, slot_start: datetime.datetime, slot_end: datetime.datetime
    ):
        try:
            return PricingService.get_price_for_30_minutes(
                get_weekday_name(slot_start), court, slot_start.time(), slot_end.time()
            )
        except Exception:
            return 0

    @staticmethod
    def get_total_price_for_reservation(
        court: Court,
        reservation_start: datetime.datetime,
        reservation_end: datetime.datetime,
    ):
        slots = int((reservation_end - reservation_start).total_seconds() / (30 * 60))
        total_price = 0
        for slot in range(slots):
            time = (30 * 60) * slot
            price = PricingService.get_price_for_30_minutes(
                weekday=get_weekday_name(reservation_start),
                court=court,
                time_start=(
                    reservation_start + datetime.timedelta(seconds=time)
                ).time(),
                time_end=(
                    reservation_start
                    + datetime.timedelta(seconds=time)
                    + datetime.timedelta(minutes=30)
                ).time(),
            )
            total_price += price
        return total_price

    @staticmethod
    def validate(court: Court, start: datetime.datetime, end: datetime.datetime):
        if not start < end or is_minimum_30_minutes(start, end):
            raise IncorrectTimeException
        if not ReservationService.is_available(court, start, end):
            raise CourtBusyException

    @staticmethod
    @transaction.atomic
    def create(
        court: Court, user: CustomUser, start: datetime.datetime, end: datetime.datetime
    ) -> Reservation:
        ReservationService.validate(court, start, end)
        return Reservation.objects.create(
            court=court, user=user, start_datetime=start, end_datetime=end
        )
