from drf_spectacular.utils import extend_schema
from rest_framework.decorators import parser_classes
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet
from rest_framework.request import Request
from rest_framework.response import Response

from profiles.models import Profile
from profiles.serializers import AvatarSerializer
from users.permissions import IsSelf


class AvatarViewset(GenericViewSet, CreateModelMixin):
    queryset = Profile.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, IsSelf]

    def get_serializer_class(self):
        return AvatarSerializer

    @extend_schema(request=AvatarSerializer, tags=["Users"])
    def create(self, request: Request, pk=None) -> Response:
        profile = Profile.objects.get(pk=pk)
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile.avatar = serializer.validated_data["avatar"]
        profile.save()
        return Response(status=HTTP_201_CREATED, data="Image uploaded successfully")
