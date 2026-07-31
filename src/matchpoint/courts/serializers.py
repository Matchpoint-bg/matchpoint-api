from rest_framework import serializers
from .models import Court


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = "__all__"


class CourtOpeningSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    available = serializers.BooleanField()
    price = serializers.FloatField()


class AvailableCourtQuerySerializer(serializers.Serializer):
    date = serializers.DateField(
        help_text="Date for which the availability should be returned (format YYYY-MM-DD)"
    )
