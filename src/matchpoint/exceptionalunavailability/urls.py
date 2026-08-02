from django.urls import include, path
from rest_framework.routers import DefaultRouter

from exceptionalunavailability.views import ExceptionalUnavailabilityViewset

router = DefaultRouter()
router.register(r"unavailabilities", ExceptionalUnavailabilityViewset)

urlpatterns = [path("", include(router.urls))]
