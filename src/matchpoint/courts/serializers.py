from rest_framework import serializers
from .models import Court, CourtImages


class CourtOpeningSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    available = serializers.BooleanField()
    price = serializers.FloatField()


class AvailableCourtQuerySerializer(serializers.Serializer):
    date = serializers.DateField(
        help_text="Date for which the availability should be returned (format YYYY-MM-DD)"
    )


class CourtImageSerailizer(serializers.ModelSerializer):
    class Meta:
        model = CourtImages
        fields = ["image"]


class CourtSerializer(serializers.ModelSerializer):
    images = CourtImageSerailizer(many=True, read_only=True)

    class Meta:
        model = Court
        fields = "__all__"
