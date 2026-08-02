from rest_framework.serializers import ModelSerializer

from exceptionalunavailability.models import ExceptionalUnavailability


class ExceptionalUnavailabilitySerializer(ModelSerializer):
    class Meta:
        model = ExceptionalUnavailability
        fields = ["pk", "start_datetime", "end_datetime"]
