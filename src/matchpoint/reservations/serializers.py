from rest_framework import serializers

from reservations.models import Reservation


class ReservationCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["court", "start_datetime", "end_datetime"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            "id",
            "court",
            "user",
            "start_datetime",
            "end_datetime",
            "reservation_amt",
        )
