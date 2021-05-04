from rest_framework import serializers

from manager.models import BaseTaskLogModel, TaskModel, TaskSequenceModel
from manager.models import BaseTaskModel
from manager.models import TaskStatusModel
from rest.utils.serializer import CustomSerializer


class TaskStatusSerializer(CustomSerializer):
    class Meta:
        model = TaskStatusModel
        fields = "__all__"


class BaseTaskSerializer(CustomSerializer):
    class Meta:
        model = BaseTaskModel
        fields = "__all__"


class BaseTaskLogSerializer(CustomSerializer):
    base_task = BaseTaskSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = BaseTaskLogModel
        fields = "__all__"


class TaskSerializer(CustomSerializer):

    class Meta:
        model = TaskModel
        fields = "__all__"


class TaskSequenceSerializer(CustomSerializer):
    base_task = BaseTaskSerializer()
    task = TaskSerializer()

    class Meta:
        model = TaskSequenceModel
        fields = "__all__"
