# Create your views here.

from rest_framework.viewsets import ModelViewSet

from pricings.models import Prices
from pricings.serializers import PricesSerializer


class PricingViewset(ModelViewSet):
    queryset = Prices.objects.all()
    serializer_class = PricesSerializer
