from rest_framework import serializers

from manager.models import BaseTaskLogModel
from manager.models import BaseTaskModel
from manager.models import TaskStatusModel
from collections import OrderedDict
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatusModel
        fields = "__all__"


class BaseTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseTaskModel
        fields = "__all__"


class BaseTaskLogSerializer(serializers.ModelSerializer):
    base_task = BaseTaskSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = BaseTaskLogModel
        fields = "__all__"
        
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields
        model = instance._meta.model
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            model_field = model._meta.get_field(field.field_name)
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = {"self": None, "link": None} if model_field.is_relation else None
            else:
                ret[field.field_name] = {"self": field.to_representation(attribute), "link": None} if model_field.is_relation else field.to_representation(attribute)
        return ret