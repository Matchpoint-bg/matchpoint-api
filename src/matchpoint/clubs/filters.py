from django_filters import rest_framework as filters
from courts.models import Court
from clubs.models import Club


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
