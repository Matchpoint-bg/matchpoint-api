from django_filters import rest_framework as filters
from common.exceptions import NoOpeningTimesFound
from courts.models import Court
from clubs.models import Club
from reservations.services import ReservationService


class ClubFilter(filters.FilterSet):
    class Meta:
        model = Club
        fields = ["city", "name", "post_code", "latitude", "longitude"]

    city = filters.CharFilter()
    name = filters.CharFilter(lookup_expr="icontains")
    post_code = filters.CharFilter()
    latitude = filters.NumberFilter()
    longitude = filters.NumberFilter()
    surface = filters.ChoiceFilter(
        field_name="courts__surface_type", choices=Court.CourtType.choices
    )
    sport = filters.ChoiceFilter(
        field_name="courts__sport_type", choices=Court.SportType.choices
    )
    is_indoor = filters.BooleanFilter(field_name="courts__is_indoor")
    date = filters.DateFilter(method="filter_date")

    def filter_date(self, queryset, name, value):
        available_clubs = []

        for club in queryset.prefetch_related("courts"):
            for court in club.courts.all():
                try:
                    res = [
                        obj
                        for obj in ReservationService.get_availability(court, value)
                        if obj["available"]
                    ]
                    if any(res):
                        available_clubs.append(club.pk)
                        break
                except NoOpeningTimesFound:
                    break

        return queryset.filter(pk__in=available_clubs)
