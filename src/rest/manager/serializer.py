from rest_framework_recursive.fields import RecursiveField

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
from rest.utils.serializers import CustomSerializer


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


class ModuleSerializer(CustomSerializer):
    class Meta:
        model = ModuleModel
        fields = "__all__"


class MethodModuleSerializer(CustomSerializer):
    module = ModuleSerializer(required=False)

    class Meta:
        model = MethodModuleModel
        fields = "__all__"


class ActionSerializer(CustomSerializer):
    task = TaskSerializer()
    method = MethodModuleSerializer()

    class Meta:
        model = ActionModel
        fields = "__all__"


class TaskLogSerializer(CustomSerializer):
    main_task_log = BaseTaskLogSerializer()
    action = ActionSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = TaskLogModel
        fields = "__all__"


class CommandSerializer(CustomSerializer):
    action = ActionSerializer()
    method = MethodModuleSerializer()
    parent = RecursiveField()

    class Meta:
        model = CommandModel
        fields = "__all__"


class CommandLogSerializer(CustomSerializer):
    task_log = TaskLogSerializer()
    parent = RecursiveField()
    command = CommandSerializer()
    status = TaskStatusSerializer()

    class Meta:
        model = CommandLogModel
        fields = "__all__"


class MessageSerializer(CustomSerializer):
    task_log = TaskLogSerializer()
    command_log = CommandLogSerializer()
    parent_msg = RecursiveField()
    sender = ModuleSerializer()
    recipient = ModuleSerializer()

    class Meta:
        model = MessageModel
        fields = "__all__"
