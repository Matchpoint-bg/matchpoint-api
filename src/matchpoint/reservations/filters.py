from django_filters import rest_framework as filters

from reservations.models import Reservation


class ReservationFilter(filters.FilterSet):
    class Meta:
        model = Reservation
        fields = ["date"]

    date = filters.DateFilter(field_name="start_datetime", lookup_expr="date")
    date_after = filters.DateFilter(
        field_name="start_datetime", lookup_expr="date__gte"
    )
