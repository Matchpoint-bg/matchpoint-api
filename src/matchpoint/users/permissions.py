from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

UserModel = get_user_model()


class IsSelf(BasePermission):
    def has_object_permission(
        self, request: Request, view: APIView, obj: UserModel
    ) -> bool:
        return request.user == obj
