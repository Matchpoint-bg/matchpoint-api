from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.status import HTTP_201_CREATED
from common.exceptions import CourtBusyException
from reservations.filters import ReservationFilter
from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreationSerializer,
    ReservationSerializer,
)
from rest_framework.request import Request
from rest_framework.response import Response
from .permissions import IsStaffOrReservationOwner
from typing import Any
from .services import ReservationService


@extend_schema_view(
    list=extend_schema(
        summary="List reservations",
        description="List the reservations of the current user, or all users if current user is part of staff",
        responses={200: ReservationSerializer(many=True)},
        tags=["Reservations"],
    ),
    retrieve=extend_schema(
        summary="Get reservation",
        description="Retrieve a specific reservation by its ID",
        responses={200: ReservationSerializer},
        tags=["Reservations"],
    ),
    create=extend_schema(
        summary="Create reservation",
        description="Create a reservation",
        request=ReservationCreationSerializer,
        responses={200: ReservationSerializer},
        tags=["Reservations"],
    ),
    update=extend_schema(
        summary="Update a reservation",
        description="Update a reservation",
        request=ReservationCreationSerializer,
        responses={200: ReservationSerializer},
        tags=["Reservations"],
    ),
    partial_update=extend_schema(
        summary="Update a reservation (partial update)",
        description="Update a reservation",
        request=ReservationCreationSerializer,
        responses={200: ReservationSerializer},
        tags=["Reservations"],
    ),
    destroy=extend_schema(
        summary="Delete a reservation",
        description="Delete a reservation",
        tags=["Reservations"],
    ),
)
class ReservationViewset(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReservationOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReservationFilter

    def get_serializer_class(self, *args: Any, **kwargs: Any):
        if self.action in ("create", "update", "partial_update"):
            return ReservationCreationSerializer
        return ReservationSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if not request.user.is_staff:
            self.queryset = Reservation.objects.filter(user=request.user.id)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if not request.user.is_staff:
            self.queryset = Reservation.objects.filter(user=request.user.id)
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer) -> None:
        court = serializer.validated_data["court"]
        start_datetime = serializer.validated_data["start_datetime"]
        end_datetime = serializer.validated_data["end_datetime"]

        price = ReservationService.get_total_price_for_reservation(
            court, start_datetime, end_datetime
        )

        return serializer.save(user=self.request.user, reservation_amt=price)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        court = serializer.validated_data["court"]
        if not ReservationService.is_available(
            court,
            serializer.validated_data["start_datetime"],
            serializer.validated_data["end_datetime"],
        ):
            raise CourtBusyException
        obj = self.perform_create(serializer)
        return Response(data=ReservationSerializer(obj).data, status=HTTP_201_CREATED)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        reservation = self.get_object()
        serializer = self.get_serializer(instance=reservation, data=request.data)
        serializer.is_valid(raise_exception=True)
        info = serializer.validated_data
        if not ReservationService.is_available(
            info["court"], info["start_datetime"], info["end_datetime"], reservation.pk
        ):
            raise CourtBusyException

        self.perform_update(serializer)
        return Response(serializer.data)
