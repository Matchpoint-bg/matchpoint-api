from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from clubs.permissions import IsClubEmployeeOrAdmin
from common.serializers import ErrorSerializer
from courts.serializers import (
    AvailableCourtQuerySerializer,
    CourtOpeningSerializer,
    CourtSerializer,
)
from .models import Court
from reservations.services import ReservationService


@extend_schema_view(
    create=extend_schema(
        summary="Create a court",
        description="Create a court. Only available to club employees and admins.",
        request=CourtSerializer,
        responses={201: CourtSerializer, 401: ErrorSerializer, 403: ErrorSerializer},
    ),
    retrieve=extend_schema(
        summary="Retrieve a court",
        description="Retrieve the details of a court based on the PK in the URL.",
        responses={200: CourtSerializer, 404: ErrorSerializer},
    ),
    update=extend_schema(
        summary="Update the details of a court",
        description="Update the details of the court which PK is in the URL.",
        request=CourtSerializer,
        responses={
            200: CourtSerializer,
            404: ErrorSerializer,
            401: ErrorSerializer,
            403: ErrorSerializer,
        },
    ),
    partial_update=extend_schema(
        summary="Update the details of a court",
        description="Update the details of the court which PK is in the URL.",
        request=CourtSerializer,
        responses={
            200: CourtSerializer,
            404: ErrorSerializer,
            401: ErrorSerializer,
            403: ErrorSerializer,
        },
    ),
    destroy=extend_schema(
        summary="Delete a court",
        description="Delete a court which PK is in the URL. Only available to employees and admins",
    ),
)
class CourtViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsClubEmployeeOrAdmin()]
        return []

    @extend_schema(
        summary="Retrieve the court's availabilities for a given date",
        parameters=[AvailableCourtQuerySerializer],
        responses={200: CourtOpeningSerializer(many=True)},
    )
    @action(
        methods=["get"],
        detail=True,
        url_path="availabilities",
        url_name="court-availabilities",
    )
    def get_court_availabilities(self, request: Request, pk=None) -> Response:
        query_serializer = AvailableCourtQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        date = query_serializer.validated_data["date"]
        court = Court.objects.get(pk=pk)
        if pk is not None:
            slots = ReservationService.get_availability(court=court, date=date)
            serializer = CourtOpeningSerializer(slots, many=True)
        else:
            return Response()
        return Response(data=serializer.data)
