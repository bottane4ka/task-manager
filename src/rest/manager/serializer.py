from rest_framework import serializers

from manager.models import TaskStatusModel


class TaskStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskStatusModel
        fields = "__all__"