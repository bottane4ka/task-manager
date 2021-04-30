from rest_framework import viewsets

from manager.models import TaskStatusModel
from manager.models import BaseTaskModel
from manager.models import BaseTaskLogModel

from manager.serializer import TaskStatusSerializer
from manager.serializer import BaseTaskSerializer
from manager.serializer import BaseTaskLogSerializer

from rest.utils.mixins import CustomFilterModelMixin


class TaskStatusViewSet(CustomFilterModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TaskStatusModel.objects.all()
    serializer_class = TaskStatusSerializer


class BaseTaskViewSet(CustomFilterModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BaseTaskModel.objects.all()
    serializer_class = BaseTaskSerializer


class BaseTaskLogViewSet(CustomFilterModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BaseTaskLogModel.objects.all()
    serializer_class = BaseTaskLogSerializer
