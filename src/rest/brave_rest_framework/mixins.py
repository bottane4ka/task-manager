from collections import OrderedDict

from rest_framework import status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SkipField, empty
from rest_framework.relations import PKOnlyObject
from rest_framework.response import Response
from rest_framework.reverse import reverse

from rest.brave_rest_framework.exceptions import GetObjectException, FilterException


class CustomCreateModelMixin(mixins.CreateModelMixin):
    pass


class CustomRetrieveModelMixin:
    def retrieve(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (GetObjectException, FilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class CustomListModelMixin:
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (GetObjectException, FilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)


class CustomUpdateModelMixin:
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset(**kwargs)
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (GetObjectException, FilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        serializer.save()


class CustomDestroyModelMixin:
    def destroy(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            self.perform_destroy(queryset)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (GetObjectException, FilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        instance.delete()


class CustomDeserializationMixin:
    def run_validation(self, data):
        model_field = (
            self.parent.Meta.model._meta.get_field(self.source) if self.parent else None
        )
        data = empty if not data else data
        if model_field and data and isinstance(data, dict) and model_field.many_to_one:
            if "self" in data.keys():
                data = data["self"]
            pk_name = model_field.related_model._meta.pk.name
            pk_data = data.get(pk_name)
            if not pk_data:
                raise ValidationError(detail=f"KeyError, key '{pk_name}' not found.")
            try:
                validated_value = model_field.related_model.objects.get(
                    **{pk_name: pk_data}
                )
            except model_field.related_model.DoesNotExist as ex:
                raise ValidationError(
                    detail=f"Destination {data} matching query does not exist."
                )
        else:
            validated_value = super(CustomDeserializationMixin, self).run_validation(
                data
            )

        return validated_value


class CustomSerializationMixin:
    def to_representation(self, instance):
        max_level = int(self.context.get("max_level", 1))
        model = instance._meta.model

        if max_level == 0:
            if not self.source:
                raise FilterException(
                    model._meta.object_name, "параметр max_level не может быть равен 0"
                )
            return {"link": self._get_link(instance), "self": None}

        self.context["max_level"] = max_level - 1
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            model_field = model._meta.get_field(field.field_name)
            check_for_none = (
                attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            )
            if check_for_none is None:
                ret[field.field_name] = (
                    {"link": None, "self": None} if model_field.is_relation else None
                )
            else:
                ret[field.field_name] = field.to_representation(attribute)
        self.context["max_level"] += 1
        return {"link": self._get_link(instance), "self": ret} if self.source else ret

    def _get_link(self, instance):
        pk_name = instance._meta.pk.name
        url = reverse(f"{self.Meta.model._meta.db_tablespace}_{self.Meta.model._meta.db_table}_detail")
        return f"{url}?{pk_name}={instance.pk}"
