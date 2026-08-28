from rest_framework import serializers


class AccessSerializer(serializers.Serializer):
    has_access = serializers.BooleanField()
