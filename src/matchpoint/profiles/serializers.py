from rest_framework import serializers

from profiles.models import Profile


# This class should be extended with new attributes of the Profile model
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar"]


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar"]
