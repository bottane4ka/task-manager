from rest_framework import viewsets

from manager.models import BaseTaskLogModel
from manager.models import BaseTaskModel
from manager.models import TaskModel
from manager.models import TaskStatusModel
from manager.models import TaskSequenceModel
from manager.serializer import BaseTaskLogSerializer
from manager.serializer import BaseTaskSerializer
from manager.serializer import TaskSerializer
from manager.serializer import TaskStatusSerializer
from manager.serializer import TaskSequenceSerializer
from rest.utils.mixins import CustomFilterModelMixin


class TaskStatusViewSet(CustomFilterModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TaskStatusModel.objects.all()
    serializer_class = TaskStatusSerializer


class BaseTaskViewSet(CustomFilterModelMixin, viewsets.ModelViewSet):
    queryset = BaseTaskModel.objects.all()
    serializer_class = BaseTaskSerializer


class BaseTaskLogViewSet(CustomFilterModelMixin, viewsets.ModelViewSet):
    queryset = BaseTaskLogModel.objects.all()
    serializer_class = BaseTaskLogSerializer


class TaskViewSet(CustomFilterModelMixin, viewsets.ModelViewSet):
    queryset = TaskModel.objects.all()
    serializer_class = TaskSerializer


class TaskSequenceViewSet(CustomFilterModelMixin, viewsets.ModelViewSet):
    queryset = TaskSequenceModel.objects.all()
    serializer_class = TaskSequenceSerializer

