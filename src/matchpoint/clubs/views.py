from dj_rest_auth.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import QuerySet
from rest_framework.decorators import action, api_view
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from clubs.filters import ClubFilter
from clubs.permissions import IsClubEmployeeOrAdmin
from openinghours.models import OpeningHours
from openinghours.serializers import OpeningHoursSerializer
from users.serializers import UserListSerializer
from .models import Club
from .serializers import ClubSerializer, ExternalClubSerializer
from courts.serializers import CourtSerializer
from common.serializers import ErrorSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List clubs",
        description="""
Returns a list of all the clubs in the app.

There are several filters available:
    
    - city: Search by the name of the city of the club
    - post_code: Search by the post code of the club
    - name: Search by the name of the club (doesn't have to be a perfect match)
    - latitude & longitude: search by latitude and longitude. In that case, we calculate the distance of the club based to the given values.
      By default, all clubs with a distance greater than 10km will be excluded
""",
    ),
    retrieve=extend_schema(
        summary="Retrieve a club",
        description="Retrieve a specific club based on the PK provided in the path.",
    ),
    update=extend_schema(
        summary="Update a club",
        description="Update the details of a club. The action can only be performed by the staff of the club or by an admin.",
    ),
    partial_update=extend_schema(
        summary="Update a club",
        description="Update the details of a club. The action can only be performed by the staff of the club or by an admin.",
    ),
)
class ClubViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClubFilter

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()

        lat = self.request.query_params.get("lat")
        long = self.request.query_params.get("long")

        if lat and long:
            pass
        elif (lat and not long) or (long and not lat):
            raise Exception

        return queryset.distinct()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "employees"):
            return [IsAuthenticated(), IsClubEmployeeOrAdmin()]
        return []

    def get_serializer_class(self):
        if self.action == "list":
            return ExternalClubSerializer
        club = self.get_object()
        if self.request.user in club.employees.all() or self.request.user.is_staff:
            return ClubSerializer
        return ClubSerializer

    @extend_schema(
        summary="Retrieve the courts of a club",
        description="Retrieves all the courts of a specific club which PK is provided in the URL.",
    )
    @action(methods=["get"], detail=True, url_name="get-club-courts")
    def courts(self, request: Request, pk=None) -> Response:
        club = self.get_object()
        serializer = CourtSerializer(club.courts.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Retrieve the employees of a club",
        description="Retrieves the employees of a specific club which PK is provided in the URL. The endpoint is available to club employees and admins.",
        responses={201: UserListSerializer(many=True), 403: ErrorSerializer},
    )
    @action(
        methods=["get"],
        detail=True,
        permission_classes=[IsClubEmployeeOrAdmin, IsAdminUser],
        url_name="get-club-employees",
    )
    def employees(self, request: Request, pk=None) -> Response:
        club: Club = self.get_object()
        serializer = UserListSerializer(club.employees.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=["GET"],
        summary="Retrieve the opening hours",
        description="Retrieve the opening hours of a specific club",
        responses={200: OpeningHoursSerializer(many=True)},
    )
    @extend_schema(
        methods=["POST"],
        summary="Create an opening hour",
        description="Create an opening hour for a specific club",
        request=OpeningHoursSerializer,
    )
    @action(
        methods=["get", "post"],
        detail=True,
        permission_classes=[IsClubEmployeeOrAdmin],
        url_name="opening-hours",
        url_path="opening-hours",
    )
    def opening_hours(self, request: Request, pk=None) -> Response:
        club = self.get_object()

        if self.request.method == "GET":
            opening_hours = OpeningHours.objects.filter(club=club).all()
            serializer = OpeningHoursSerializer(opening_hours, many=True)
            return Response(data=serializer.data)

        serializer = OpeningHoursSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        OpeningHours.objects.create(
            club=club,
            weekday=serializer.validated_data["weekday"],
            opening_hour=serializer.validated_data["opening_hour"],
            closing_hour=serializer.validated_data["closing_hour"],
        )

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
