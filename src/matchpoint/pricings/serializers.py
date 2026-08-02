from rest_framework.serializers import ModelSerializer

from pricings.models import Prices


class PricesSerializer(ModelSerializer):
    class Meta:
        model = Prices
        fields = "__all__"


# Same serializer as the one above, but used when calling from a court-related view, as the court ID is in the URI
class CourtsPricesSerializer(ModelSerializer):
    class Meta:
        model = Prices
        fields = ["weekday", "time_start", "time_end", "price_per_30_minutes"]
