from rest_framework.mixins import CreateModelMixin
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet
from rest_framework.request import Request
from rest_framework.response import Response

from profiles.models import Profile
from profiles.serializers import AvatarSerializer


class AvatarViewset(GenericViewSet, CreateModelMixin):
    def create(self, request: Request, pk=None) -> Response:
        profile = Profile.objects.get(pk=pk)
        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile.avatar = serializer.validated_data["avatar"]
        profile.save()
        return Response(status=HTTP_201_CREATED, data=serializer.data)
