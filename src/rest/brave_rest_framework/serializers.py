from rest_framework.serializers import ModelSerializer

from rest.brave_rest_framework.mixins import (
    CustomSerializationMixin,
    CustomDeserializationMixin,
)


class CustomSerializer(
    CustomDeserializationMixin, CustomSerializationMixin, ModelSerializer
):
    pass
