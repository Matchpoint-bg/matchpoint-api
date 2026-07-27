from rest_framework import permissions, viewsets
from rest_framework.status import HTTP_201_CREATED
from common.exceptions import CourtBusyException, IncorrectTimeException
from rest_framework.serializers import BaseSerializer
from common.helpers import is_30_minutes_increment
from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreationSerializer,
    ReservationsSerializer,
)
from rest_framework.request import Request
from rest_framework.response import Response
from .permissions import IsStaffOrReservationOwner
from typing import Any
from .services import ReservationService


class ReservationViewset(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationsSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReservationOwner]

    def get_serializer_class(self, *args: Any, **kwargs: Any):
        if self.action in ("create", "update", "partial_update"):
            return ReservationCreationSerializer
        return ReservationsSerializer

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

        serializer.save(user=self.request.user, reservation_amt=price)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        court = serializer.validated_data["court"]
        if not is_30_minutes_increment(
            serializer.validated_data["start_datetime"]
        ) or not is_30_minutes_increment(serializer.validated_data["end_datetime"]):
            raise IncorrectTimeException
        if not ReservationService.is_available(
            court,
            serializer.validated_data["start_datetime"],
            serializer.validated_data["end_datetime"],
        ):
            raise CourtBusyException
        self.perform_create(serializer)
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        info = serializer.validated_data
        if not is_30_minutes_increment(
            info["start_datetime"]
        ) or not is_30_minutes_increment(info["end_datetime"]):
            raise IncorrectTimeException
        return super().update(request)
