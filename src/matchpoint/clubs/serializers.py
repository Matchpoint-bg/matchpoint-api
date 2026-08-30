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


class ClubListSerializer(serializers.ModelSerializer):
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
            "header_image",
        ]


class ClubImageUploadSerializer(serializers.Serializer):
    header_image = serializers.ImageField()


class ClubImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["header_image"]


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
