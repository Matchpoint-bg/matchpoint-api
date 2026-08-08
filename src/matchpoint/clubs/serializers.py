from rest_framework import serializers
from .models import Club


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "city",
            "address",
            "post_code",
            "latitude",
            "longitude",
            "description",
            "website",
            "phone",
            "email",
        ]
        # Add employees to write-only to not be displayed in list
        # extra_kwargs = {"employees": {"write_only": True}}
        #


class ExternalClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "city",
            "address",
            "post_code",
            "latitude",
            "longitude",
            "description",
            "website",
            "phone",
            "email",
        ]
