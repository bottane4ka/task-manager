from rest_framework.serializers import ModelSerializer

from rest.utils.mixins import CustomSerializationMixin, CustomDeserializationMixin


class CustomSerializer(
    CustomDeserializationMixin, CustomSerializationMixin, ModelSerializer
):
    pass
