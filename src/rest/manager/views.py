from rest_framework import viewsets
from rest_framework import mixins

from manager.models import ActionModel
from manager.models import BaseTaskLogModel
from manager.models import BaseTaskModel
from manager.models import CommandLogModel
from manager.models import CommandModel
from manager.models import MessageModel
from manager.models import MethodModuleModel
from manager.models import ModuleModel
from manager.models import TaskLogModel
from manager.models import TaskModel
from manager.models import TaskSequenceModel
from manager.models import TaskStatusModel

from manager.serializer import ActionSerializer
from manager.serializer import BaseTaskLogSerializer
from manager.serializer import BaseTaskSerializer
from manager.serializer import CommandLogSerializer
from manager.serializer import CommandSerializer
from manager.serializer import MessageSerializer
from manager.serializer import MethodModuleSerializer
from manager.serializer import ModuleSerializer
from manager.serializer import TaskLogSerializer
from manager.serializer import TaskSequenceSerializer
from manager.serializer import TaskSerializer
from manager.serializer import TaskStatusSerializer
from rest.utils import viewsets


class ActionViewSet(viewsets.CustomModelViewSet):
    queryset = ActionModel.objects.all()
    serializer_class = ActionSerializer


class CommandViewSet(viewsets.CustomModelViewSet):
    queryset = CommandModel.objects.all()
    serializer_class = CommandSerializer


class CommandLogViewSet(viewsets.CustomModelViewSet):
    queryset = CommandLogModel.objects.all()
    serializer_class = CommandLogSerializer


class MessageViewSet(viewsets.CustomModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageSerializer


class MethodModuleViewSet(viewsets.CustomModelViewSet):
    queryset = MethodModuleModel.objects.all()
    serializer_class = MethodModuleSerializer


class ModuleViewSet(viewsets.CustomModelViewSet):
    queryset = ModuleModel.objects.all()
    serializer_class = ModuleSerializer


class TaskLogViewSet(viewsets.CustomModelViewSet):
    queryset = TaskLogModel.objects.all()
    serializer_class = TaskLogSerializer


class TaskStatusViewSet(viewsets.CustomReadOnlyModelViewSet):
    queryset = TaskStatusModel.objects.all()
    serializer_class = TaskStatusSerializer


class BaseTaskViewSet(viewsets.CustomModelViewSet):
    queryset = BaseTaskModel.objects.all()
    serializer_class = BaseTaskSerializer


class BaseTaskLogViewSet(viewsets.CustomModelViewSet):
    queryset = BaseTaskLogModel.objects.all()
    serializer_class = BaseTaskLogSerializer


class TaskViewSet(viewsets.CustomModelViewSet):
    queryset = TaskModel.objects.all()
    serializer_class = TaskSerializer


class TaskSequenceViewSet(viewsets.CustomModelViewSet):
    queryset = TaskSequenceModel.objects.all()
    serializer_class = TaskSequenceSerializer
