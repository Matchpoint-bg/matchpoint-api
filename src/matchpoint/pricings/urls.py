from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pricings.views import PricingViewset


router = DefaultRouter()
router.register(r"pricing", PricingViewset)

urlpatterns = [path("", include(router.urls))]
