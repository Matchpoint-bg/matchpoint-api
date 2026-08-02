# Create your views here.

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from clubs.permissions import IsClubEmployeeOrAdmin
from pricings.models import Prices
from pricings.serializers import CourtsPricesSerializer


@extend_schema_view(
    update=extend_schema(summary="Update a specific pricing"),
    partial_update=extend_schema(summary="Update a specific pricing (partial update)"),
    destroy=extend_schema(summary="Delete a specific pricing"),
)
class PricingViewset(GenericViewSet, DestroyModelMixin, UpdateModelMixin):
    queryset = Prices.objects.all()
    serializer_class = CourtsPricesSerializer
    permission_classes = [IsAuthenticated, IsClubEmployeeOrAdmin]
