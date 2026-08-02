# Create your views here.
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from clubs.permissions import IsClubEmployeeOrAdmin
from exceptionalunavailability.models import ExceptionalUnavailability
from exceptionalunavailability.serializers import ExceptionalUnavailabilitySerializer


class ExceptionalUnavailabilityViewset(
    GenericViewSet, DestroyModelMixin, UpdateModelMixin
):
    permission_classes = [IsAuthenticated, IsClubEmployeeOrAdmin]
    queryset = ExceptionalUnavailability.objects.all()
    serializer_class = ExceptionalUnavailabilitySerializer
