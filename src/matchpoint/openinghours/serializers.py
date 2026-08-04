from rest_framework.serializers import ModelSerializer

from openinghours.models import OpeningHours


class OpeningHoursSerializer(ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = ["pk", "weekday", "opening_hour", "closing_hour"]


class UpdateOpeningHoursSerializer(ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = ["weekday", "opening_hour", "closing_hour"]
