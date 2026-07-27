from rest_framework import serializers

from reservations.models import Reservation


class ReservationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"


class ReservationCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["court", "start_datetime", "end_datetime"]
