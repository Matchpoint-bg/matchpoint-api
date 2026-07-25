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
