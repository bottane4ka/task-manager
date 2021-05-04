from collections import OrderedDict

from rest_framework.fields import SkipField, empty
from rest_framework.relations import PKOnlyObject
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer

from rest.utils.exceptions import FilterException


class CustomSerializer(ModelSerializer):

    def __init__(self, instance=None, data=empty, **kwargs):
        super(CustomSerializer, self).__init__(instance=instance, data=data, **kwargs)

    def to_representation(self, instance):
        max_level = int(self.context.get("max_level", 1))
        model = instance._meta.model

        if max_level == 0:
            if not self.source:
                raise FilterException(model._meta.object_name, "параметр max_level не может быть равен 0")
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
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = {"link": None, "self": None} if model_field.is_relation else None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        self.context["max_level"] += 1
        return {"link": self._get_link(instance), "self": ret} if self.source else ret

    def _get_link(self, instance):
        pk_name = instance._meta.model._meta.pk.name
        url = reverse(f"{self.source}_detail")
        return f"{url}?{pk_name}={instance.pk}"

