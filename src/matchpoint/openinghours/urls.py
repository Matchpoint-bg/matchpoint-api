from rest_framework.routers import DefaultRouter
from django.urls import include, path
from openinghours.views import OpeningHoursViewset

router = DefaultRouter()
router.register(r"openinghours", OpeningHoursViewset, basename="openinghours")

urlpatterns = [path("", include(router.urls))]
