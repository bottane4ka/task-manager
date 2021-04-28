from rest_framework import viewsets, mixins

from manager.models import TaskStatusModel
from manager.serializer import TaskStatusSerializer
from rest_framework import decorators
from rest_framework.response import Response


class TaskStatusViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = TaskStatusModel.objects.all()
    serializer_class = TaskStatusSerializer

