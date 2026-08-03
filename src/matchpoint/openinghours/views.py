from drf_spectacular.utils import extend_schema, extend_schema_view
from openinghours.models import OpeningHours
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from clubs.permissions import IsClubEmployeeOrAdmin
from openinghours.serializers import (
    UpdateOpeningHoursSerializer,
)


@extend_schema_view(
    destroy=extend_schema(
        summary="Delete an opening hours entry",
    ),
    update=extend_schema(
        summary="Update an opening hours entry", request=UpdateOpeningHoursSerializer
    ),
    partial_update=extend_schema(
        summary="Update an opening hours entry (partial)",
        request=UpdateOpeningHoursSerializer,
    ),
)
class OpeningHoursViewset(GenericViewSet, DestroyModelMixin, UpdateModelMixin):
    queryset = OpeningHours.objects.all()
    serializer_class = UpdateOpeningHoursSerializer
    permission_classes = [IsClubEmployeeOrAdmin]
