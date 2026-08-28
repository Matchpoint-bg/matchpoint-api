from django.shortcuts import render
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from clubs.models import Club
from internal.serializers import AccessSerializer


@extend_schema(
    description="Endpoint which indicates if the logged in user has access to the club. Use this endpoint internally, to check the access for analytics for example",
    parameters=[
        OpenApiParameter(
            "id",
            location="path",
            type=int,
            required=True,
            description="The ID of the club to check the access of",
        )
    ],
    responses={200: AccessSerializer},
)
@api_view()
def user_has_access_to_club(request: Request, pk=None) -> Response:
    user = request.user
    club = Club.objects.filter(pk=pk)
    if club.count() == 0:
        return Response(status=HTTP_404_NOT_FOUND, data={"message": "Club not found"})
    has_access = AccessSerializer(
        data={"has_access": user in club.first().employees.all() or False}
    )
    has_access.is_valid(raise_exception=True)

    return Response(data=has_access.data)
