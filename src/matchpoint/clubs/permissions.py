from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import Any
from courts.models import Court
from clubs.models import Club


class IsClubEmployeeOrAdmin(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if isinstance(obj, Club):
            return (
                obj.employees.filter(pk=request.user.pk).exists()
                or request.user.is_staff
            )
        elif isinstance(obj, Court):
            return (
                obj.club_id.employees.filter(pk=request.user.pk).exists()
                or request.user.is_staff
            )
