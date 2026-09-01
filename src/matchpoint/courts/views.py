from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from clubs.permissions import IsClubEmployeeOrAdmin
from common.serializers import ErrorSerializer
from courts.serializers import (
    AvailableCourtQuerySerializer,
    CourtImageSerailizer,
    CourtOpeningSerializer,
    CourtSerializer,
)
from clubs.models import Club
from exceptionalunavailability.models import ExceptionalUnavailability
from exceptionalunavailability.serializers import ExceptionalUnavailabilitySerializer
from pricings.models import Prices
from pricings.serializers import CourtsPricesSerializer
from .models import Court, CourtImages
from reservations.services import ReservationService


@extend_schema_view(
    create=extend_schema(
        summary="Create a court",
        description="Create a court. Only available to club employees and admins.",
        request=CourtSerializer,
        responses={201: CourtSerializer, 401: ErrorSerializer, 403: ErrorSerializer},
        tags=["Courts"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a court",
        description="Retrieve the details of a court based on the PK in the URL.",
        responses={200: CourtSerializer, 404: ErrorSerializer},
        tags=["Courts"],
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
        tags=["Courts"],
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
        tags=["Courts"],
    ),
    destroy=extend_schema(
        summary="Delete a court",
        description="Delete a court which PK is in the URL. Only available to employees and admins",
        tags=["Courts"],
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
    permission_action_classes = {
        "create": [IsAuthenticated, IsClubEmployeeOrAdmin],
        "update": [IsAuthenticated, IsClubEmployeeOrAdmin],
        "partial_update": [IsAuthenticated, IsClubEmployeeOrAdmin],
        "destroy": [IsAuthenticated, IsClubEmployeeOrAdmin],
        "prices": [IsAuthenticated, IsClubEmployeeOrAdmin],
        "employees": [IsAuthenticated, IsClubEmployeeOrAdmin],
        "unavailabilities": [IsAuthenticated, IsClubEmployeeOrAdmin],
    }

    permission_classes = [AllowAny]

    def get_permissions(self):
        permission_classes = self.permission_action_classes.get(
            self.action, self.permission_classes
        )
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Retrieve the court's availabilities for a given date",
        parameters=[AvailableCourtQuerySerializer],
        responses={200: CourtOpeningSerializer(many=True)},
        tags=["Courts"],
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
        court = self.get_object()
        slots = ReservationService.get_availability(court=court, date=date)
        serializer = CourtOpeningSerializer(slots, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        methods=["GET"],
        summary="Retrieve the court's prices",
        responses={200: CourtsPricesSerializer(many=True)},
        tags=["Courts"],
    )
    @extend_schema(
        methods=["PUT"],
        summary="Add prices for the court",
        description="Create prices for the selected court. WARNING: the existing prices will be deleted, so make sure you don't append data, but send also the data that is not modified",
        request=CourtsPricesSerializer(many=True),
        tags=["Courts"],
    )
    @action(methods=["get", "put"], detail=True, url_path="prices", url_name="prices")
    def prices(self, request: Request, pk=None) -> Response:
        court = self.get_object()
        if self.request.method == "GET":
            prices = Prices.objects.filter(court=court).all()
            serializer = CourtsPricesSerializer(prices, many=True)
            return Response(data=serializer.data)

        Prices.objects.filter(court=court).delete()
        serializer = CourtsPricesSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        Prices.objects.bulk_create(
            Prices(
                court=court,
                weekday=price["weekday"],
                time_start=price["time_start"],
                time_end=price["time_end"],
                price_per_30_minutes=price["price_per_30_minutes"],
            )
            for price in serializer.validated_data
        )
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        methods=["PUT"],
        summary="Create unavailability for a court",
        description="Create and exceptional unavailability for the court",
        request=ExceptionalUnavailabilitySerializer,
        tags=["Courts"],
    )
    @extend_schema(
        methods=["GET"],
        summary="Get court's unavailabilities",
        description="Retrieves the unavailabilities of a court",
        responses={200: ExceptionalUnavailabilitySerializer},
        tags=["Courts"],
    )
    @action(
        methods=["get", "put"],
        detail=True,
        url_path="unavailabilities",
        url_name="unavailabilities",
    )
    def unavailabilities(self, request: Request, pk=None) -> Response:
        court = self.get_object()

        if self.request.method == "GET":
            unavailabilities = ExceptionalUnavailability.objects.filter(
                court=court
            ).all()
            serializer = ExceptionalUnavailabilitySerializer(
                unavailabilities, many=True
            )
            return Response(data=serializer.data)

        serializer = ExceptionalUnavailabilitySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        club = Club.objects.get(pk=court.club_id.pk)
        ExceptionalUnavailability.objects.create(
            club=club,
            court=court,
            start_datetime=serializer.validated_data["start_datetime"],
            end_datetime=serializer.validated_data["end_datetime"],
        )
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        methods=["POST"],
        summary="Add images to the court",
        description="Add images to the current court",
        tags=["Courts"],
        request=CourtImageSerailizer,
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="add-image",
        url_name="images",
        parser_classes=[MultiPartParser, FormParser],
    )
    def post_images(self, request: Request, pk=None) -> Response:
        court = self.get_object()
        serializer = CourtImageSerailizer(data=request.data)
        serializer.is_valid(raise_exception=True)

        CourtImages.objects.create(
            court_id=court, image=serializer.validated_data["image"]
        )

        return Response(
            status=status.HTTP_201_CREATED, data="Image uploaded successfully"
        )

    @extend_schema(
        methods=["GET"],
        summary="Get court images",
        description="Get the images of the current court",
        tags=["Courts"],
    )
    @action(methods=["get"], detail=True, url_path="images", url_name="images")
    def get_images(self, request: Request, pk=None) -> Response:
        court = self.get_object()
        images = court.images.all()
        serializer = CourtImageSerailizer(data=images, many=True)
        serializer.is_valid(raise_exception=True)

        return Response(data=serializer.data)
