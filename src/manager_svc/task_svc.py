# -*- coding: utf-8 -*-
import json
import uuid
from collections import namedtuple
from datetime import datetime

from django.db.models import Q

from manager_svc.settings import COMMAND_LOG_CHANNEL
from manager_svc.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER
from manager_svc.settings import MAIN_TASK_LOG_CHANNEL
from manager_svc.settings import MESSAGE_CHANNEL
from manager_svc.settings import MODULE_SYSTEM_NAME
from manager_svc.settings import PERIOD_TIME
from manager_svc.settings import TASK_LOG_CHANNEL
from rest.manager.models import ActionModel
from rest.manager.models import BaseTaskLogModel
from rest.manager.models import CommandLogModel
from rest.manager.models import CommandModel
from rest.manager.models import MessageModel
from rest.manager.models import MethodModuleModel
from rest.manager.models import ModuleModel
from rest.manager.models import MsgTypeChoice
from rest.manager.models import ObjectToCommandLogModel
from rest.manager.models import StatusSendChoice
from rest.manager.models import TaskLogModel
from rest.manager.models import TaskSequenceModel
from rest.manager.models import TaskStatusModel
from utils.base_utils.base_class import BaseSVC
from utils.exceptions import FindModuleError
from utils.wrapper import message_wrapper

FuncInfo = namedtuple("FuncInfo", "name max_count wait_time")


class TaskSVC(BaseSVC):
    """
    Менеджер задач

    Основные задачи:
     - подписка на каналы, указанные в настройках менеджера
     - запуск периодической задачи: проверка на работоспособность функциональных служб
     - при получении сообщений:
        - создание сообщений для соответствующих задач
        - обновление статусов отправки сообщений
        - обновление статусов выполнения задачи в соответствии с ответом сообщения

    """

    _module = None
    _notify_query = "SELECT pg_notify('{}', '{}');"
    _ksa = None
    _key_func = {
        TASK_LOG_CHANNEL: FuncInfo("refresh_task_log", 10, 10),
        COMMAND_LOG_CHANNEL: FuncInfo("refresh_command_log", 10, 10),
        MAIN_TASK_LOG_CHANNEL: FuncInfo("refresh_main_task_log", 10, 10),
        MESSAGE_CHANNEL: FuncInfo("refresh_message", 100, 10),
    }

    cursor = None
    notify_list = None

    def __init__(self, thread_count):
        BaseSVC.__init__(
            self, thread_count, DB_HOST, DB_PORT, DB_NAME, DB_USER, MODULE_SYSTEM_NAME
        )
        self.module = MODULE_SYSTEM_NAME
        self.cursor = self.e.cursor()

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, system_name: str) -> None:
        try:
            self._module = ModuleModel.objects.get(system_name=system_name)
        except ModuleModel.DoesNotExist:
            message = (
                "Службы с указанным системным наименованием не существует в базе данных"
            )
            raise FindModuleError(message)
        except ModuleModel.MultipleObjectsReturned:
            message = "Существует несколько служб с указанным системным наименованием в базе данных"
            raise FindModuleError(message)
        self._module.status = True
        self._module.save()

    def run(self):
        """
        Запуск подписки на список каналов

        Основыне задачи метода:
         - инициализация списка каналов: канал для сущности "Сообщения" и канал для сущности "Аудит выполнения задач"
         - инициализация структуры для хранения времени первого сообщения и количество сообщений
           (данная структура необходима для реализации ожидания нескольких сообщений из канала,
            обеспечивает выполнение поиска изменений не для каждого изменения в БД а для группы изменений)
         - запуск подкписки

        :return:
        """
        self.table_list = [
            MESSAGE_CHANNEL,
            TASK_LOG_CHANNEL,
            MAIN_TASK_LOG_CHANNEL,
            COMMAND_LOG_CHANNEL,
        ]
        self.notify_list = dict()
        for key, item in self._key_func.items():
            self.notify_list[key] = NotifyCount(item.max_count, item.wait_time)
        BaseSVC.run(self)

    def add_task(self, channel: str, data: str) -> None:
        """
        Обработка сообщений из каналов

        Алгоритм:
         - для каждого канала проверяется нужно ли запускать поиск изменений
           в зависимости от прошедшего времени и количества уже поступивших аналогичных сообщений
         - если нужно, то запускается соответствующий метод

        :param channel: наименование канала
        :param data: сообщение (не используется)
        :return:
        """
        if self.notify_list[channel].is_need_add_task():
            refresh_func = getattr(self, self._key_func[channel].name)
            refresh_func()

    def refresh_main_task_log(self):
        """
        Поиск изменений в сущности "Аудит выполнения базовых задач"
        :return:
        """
        main_task_log_list = BaseTaskLogModel.objects.filter(
            status_id__system_name="progress", task_log_list__isnull=True
        )
        if main_task_log_list:
            self.pool_task.add_task(self.create_task_log, main_task_log_list)

        main_task_log_list = BaseTaskLogModel.objects.filter(
            status_id__system_name="cancel", task_log_list__isnull=False
        )
        if main_task_log_list:
            self.pool_task.add_task(self.cancel_task_log, main_task_log_list)

    def refresh_task_log(self):
        """
        Поиск изменений в сущности "Аудит выполнения задач"
        :return:
        """
        task_log_list = TaskLogModel.objects.filter(
            status_id__system_name="progress",
            action_id__method_id__module_id__status=True,
        ).distinct()
        if task_log_list:
            self.pool_task.add_task(self.create_message, task_log_list)

        task_log_list = TaskLogModel.objects.filter(
            status_id__system_name="cancel",
            command_log_list__status_id__system_name__in=["set", "progress"],
        ).distinct()
        if task_log_list:
            self.pool_task.add_task(self.cancel_command_log, task_log_list)

        main_task_log = BaseTaskLogModel.objects.filter(
            status_id__system_name="progress"
        ).distinct()
        if main_task_log:
            self.pool_task.add_task(self.update_main_task_log, main_task_log)

    def refresh_command_log(self):
        """
        Поиск изменений в сущности "Аудит выполнения команд"
        :return: 
        """
        command_log_list = CommandLogModel.objects.filter(
            status_id__system_name="progress"
        ).distinct()
        if command_log_list:
            self.pool_task.add_task(
                self.create_message, command_log_list, is_command=True
            )

        command_log_list = CommandLogModel.objects.filter(
            status_id__system_name="cancel",
            command_log_list__status_id__system_name__in=["set", "progress"],
        ).distinct()
        if command_log_list:
            self.pool_task.add_task(
                self.cancel_command_log, command_log_list, is_command=True
            )

        command_log_list = (
            CommandLogModel.objects.filter(
                status_id__system_name="progress",
                command_log_list__status_id__system_name="set",
            )
            .exclude(command_log_list__status_id__system_name="error")
            .distinct()
        )
        if command_log_list:
            self.pool_task.add_task(
                self.update_next_command_log, command_log_list, is_command=True
            )

        task_log_list = (
            TaskLogModel.objects.filter(
                status_id__system_name="progress",
                command_log_list__status_id__system_name="set",
            )
            .exclude(command_log_list__status_id__system_name="error")
            .distinct()
        )
        if task_log_list:
            self.pool_task.add_task(
                self.update_next_command_log, task_log_list, is_command=False
            )

        command_log_list = CommandLogModel.objects.filter(
            status_id__system_name="progress", command_id__command_list__isnull=False
        ).distinct()
        if command_log_list:
            self.pool_task.add_task(self.update_log, command_log_list, is_command=True)

        task_log_list = TaskLogModel.objects.filter(
            status_id__system_name="progress", action_id__command_list__isnull=False
        ).distinct()
        if task_log_list:
            self.pool_task.add_task(self.update_log, task_log_list)

    def refresh_message(self):
        """
        Поиск изменений в сущности "Сообщения"
        :return:
        """
        message_list = MessageModel.objects.filter(
            Q(msg_type=MsgTypeChoice.task.value, status__isnull=True)
            | Q(
                msg_type=MsgTypeChoice.connect.value,
                send_id=self.module,
                status__isnull=True,
            )
        )
        if message_list:
            self.pool_task.add_task(self.send_notify, message_list)

        message_list = MessageModel.objects.filter(
            msg_type=MsgTypeChoice.task.value,
            status=StatusSendChoice.sent.value,
            get_id=self.module,
        )
        if message_list:
            self.pool_task.add_task(self.create_command_log, message_list)

        message_list = MessageModel.objects.filter(
            msg_type__in=[MsgTypeChoice.success.value, MsgTypeChoice.error.value],
            get_id=self.module,
            status=StatusSendChoice.sent.value,
            command_log_id__status_id__system_name="progress",
        )
        if message_list:
            self.pool_task.add_task(self.update_command_log, message_list)

        message_list = MessageModel.objects.filter(
            msg_type__in=[MsgTypeChoice.success.value, MsgTypeChoice.error.value],
            get_id=self.module,
            status=StatusSendChoice.sent.value,
            task_log_id__status_id__system_name="progress",
            command_log_id__isnull=True,
        )
        if message_list:
            self.pool_task.add_task(self.update_task_log, message_list)

        message_list = MessageModel.objects.filter(
            msg_type__in=[MsgTypeChoice.info.value, MsgTypeChoice.warning.value],
            get_id=self.module,
            status=StatusSendChoice.sent.value,
        )
        if message_list:
            self.pool_task.add_task(self.update_message, message_list)

        message_list = MessageModel.objects.filter(
            msg_type=MsgTypeChoice.connect.value,
            get_id=self.module,
            status=StatusSendChoice.sent.value,
        )
        if message_list:
            self.pool_task.add_task(self.restart_log, message_list)

    def create_task_log(self, main_task_log_list):
        """
        Постановка задач в сущности "Аудит выполнения задач" на основе базовой задачи
        :param main_task_log_list: список задач из сущности "Аудит выполнения базовых задач"
        :return:
        """
        status_set = TaskStatusModel.objects.get(system_name="set")
        status_progress = TaskStatusModel.objects.get(system_name="progress")
        for main_task_log in main_task_log_list:
            task_log_list = list()
            task_sequence_list = TaskSequenceModel.objects.filter(
                template_task_id=main_task_log.template_task_id
            ).order_by("number")
            if task_sequence_list:
                for task_sequence in task_sequence_list:
                    action_list = ActionModel.objects.filter(
                        task_id=task_sequence.task_id
                    ).order_by("number")
                    if action_list:
                        for action in action_list:
                            data = TaskLogModel(
                                main_task_log_id=main_task_log,
                                action_id=action,
                                status_id=status_set,
                            )
                            task_log_list.append(data)
            if task_log_list:
                task_log_list[0].status_id = status_progress
                TaskLogModel.objects.bulk_create(task_log_list)
            current_task = TaskLogModel.objects.filter(
                main_task_log_id=main_task_log, status_id=status_progress
            ).last()
            if current_task:
                main_task_log.current_task_id = current_task
                main_task_log.save()

    def cancel_task_log(self, main_task_log_list):
        """
        Отмена поставленных задач в сущности "Аудит выполнения задач"
        :param main_task_log_list: списокй записей из сущности "Аудит выполнения базовых задач"
        :return:
        """
        status = TaskStatusModel.objects.get(system_name="cancel")
        task_log_list = TaskLogModel.objects.filter(
            main_task_log_id__in=main_task_log_list, status_id__system_name="set"
        )
        task_log_list.update(status_id=status)

    def create_message(self, log_list, is_command=False, is_restart=False):
        """
        Создание записей в сущности "Сообщения" (Задача или Подключение)
        :param log_list: список записей из сущностей "Аудит выполнения задач" или "Аудит выполнения команд"
        :param is_command: признак того, что записи из сущности "Аудит выполнения команд"
        :param is_restart: признак перезапуска
        :return:
        """
        status = TaskStatusModel.objects.get(system_name="progress")
        for log_item in log_list:
            is_new = False
            if is_command:
                s_message = MessageModel.objects.filter(
                    task_log_id=log_item.task_log_id,
                    command_log_id=log_item,
                    msg_type=MsgTypeChoice.success.value,
                ).order_by("-date_created")
                e_message = MessageModel.objects.filter(
                    task_log_id=log_item.task_log_id,
                    command_log_id=log_item,
                    msg_type=MsgTypeChoice.error.value,
                ).order_by("-date_created")
                command_log_list = CommandLogModel.objects.filter(
                    task_log_id=log_item.task_log_id, parent_id=log_item
                )
            else:
                s_message = MessageModel.objects.filter(
                    task_log_id=log_item,
                    command_log_id__isnull=True,
                    msg_type=MsgTypeChoice.success.value,
                ).order_by("-date_created")
                e_message = MessageModel.objects.filter(
                    task_log_id=log_item,
                    command_log_id__isnull=True,
                    msg_type=MsgTypeChoice.error.value,
                ).order_by("-date_created")
                command_log_list = CommandLogModel.objects.filter(task_log_id=log_item)

            s_message = s_message.first() if s_message else None
            e_message = e_message.first() if e_message else None

            if not command_log_list:
                if (
                    s_message
                    and e_message
                    and s_message.date_created < e_message.date_created
                ):
                    is_new = True
                elif not s_message:
                    is_new = True

                if is_new:
                    method = (
                        log_item.action_id.method_id
                        if not is_command
                        else log_item.command_id.method_id
                    )
                    if method.module_id.status:
                        s_id = uuid.uuid4()
                        post_data = {
                            "s_id": s_id,
                            "send_id": self.module,
                            "get_id": method.module_id,
                            "date_created": datetime.now(),
                            "status": None,
                            "msg_type": MsgTypeChoice.task.value,
                            "parent_msg_id": None,
                            "task_log_id": log_item
                            if not is_command
                            else log_item.task_log_id,
                            "command_log_id": log_item if is_command else None,
                            "data": {
                                "task_id": str(s_id),
                                "msg_type": MsgTypeChoice.task.value,
                                "method": method.system_name,
                            },
                        }
                        MessageModel.objects.create(**post_data)
                if log_item.status_id != status:
                    log_item.status_id = status
                    log_item.save()

    def update_main_task_log(self, main_task_log_list):
        """
        Обновление статуса выполнения задач в сущности "Аудит выполнения базовых задач"
        :param main_task_log_list: список записей из сущности "Аудит выполнения базовых задач"
        :return:
        """
        f_status = TaskStatusModel.objects.get(system_name="finish")
        e_status = TaskStatusModel.objects.get(system_name="error")
        for main_task_log in main_task_log_list:
            e_command_log_list = TaskLogModel.objects.filter(
                main_task_log_id=main_task_log, status_id=e_status
            )
            not_command_log_list = TaskLogModel.objects.filter(
                Q(main_task_log_id=main_task_log) & ~Q(status_id=f_status)
            )
            if e_command_log_list:
                main_task_log.status_id = e_status
                main_task_log.save()
            elif not not_command_log_list:
                main_task_log.status_id = f_status
                main_task_log.end_task_date = datetime.now()
                main_task_log.current_task_id = None
                main_task_log.save()

    def cancel_command_log(self, log_list, is_command=False):
        """
        Отмена поставленных команд в сущности "Аудит выполнения команд"
        :param log_list: список записей из аудита выполнения
        :param is_command: признак того, что данные из сущности "Аудит выполнения команд"
        :return:
        """
        status = TaskStatusModel.objects.get(system_name="cancel")
        for log_item in log_list:
            command_log_list = log_item.command_log_list.filter(
                status_id__system_name="set"
            )
            command_log_list.update(status_id=status)
            command_log_list = log_item.command_log_list.filter(
                status_id__system_name="progress",
                command_log_list__status_id__system_name="set",
            )
            if command_log_list:
                self.cancel_command_log(command_log_list, is_command=True)

    def update_next_command_log(self, log_list, is_command=False):
        """
        Обновление следующих команд из сущности «Аудит выполнения команд»
        :param log_list: список записей из аудита выполнения
        :param is_command: признак того, что данные из сущности "Аудит выполнения команд"
        :return:
        """
        status = TaskStatusModel.objects.get(system_name="progress")
        for log_item in log_list:
            command_log = (
                log_item.command_log_list.filter(status_id__system_name="finish")
                .order_by("command_id__number")
                .last()
            )
            if command_log:
                if is_command:
                    next_command_log_list = CommandLogModel.objects.filter(
                        task_log_id=log_item.task_log_id,
                        parent_id=log_item,
                        status_id__system_name="set",
                        command_id__is_parallel=False,
                        command_id__number=command_log.command_id.number + 1,
                    )
                else:
                    next_command_log_list = CommandLogModel.objects.filter(
                        task_log_id=log_item,
                        command_id__is_parallel=False,
                        status_id__system_name="set",
                        command_id__number=command_log.command_id.number + 1,
                    )
                if next_command_log_list:
                    for next_command_log in next_command_log_list:
                        next_command_log.status_id = status
                        next_command_log.save()

    def update_log(self, log_list, is_command=False):
        """
        Обновление статуса выполнения задачи в сущностях «Аудит выполнения задач»
        или "Аудит выполнения команд"
        :param log_list: список записей из сущностей "Аудит выполнения задач" или "Аудит выполнения команд"
        :param is_command: признак того, что данные из сущности "Аудит выполнения команд"
        :return:
        """
        f_status = TaskStatusModel.objects.get(system_name="finish")
        e_status = TaskStatusModel.objects.get(system_name="error")
        for log in log_list:
            if is_command:
                command_log_list = CommandLogModel.objects.filter(parent_id=log)
            else:
                command_log_list = CommandLogModel.objects.filter(task_log_id=log)
            if command_log_list:
                e_command_log_list = command_log_list.filter(status_id=e_status)
                not_command_log_list = command_log_list.filter(~Q(status_id=f_status))
                if e_command_log_list:
                    log.status_id = e_status
                    log.save()
                elif not not_command_log_list:
                    log.status_id = f_status
                    log.save()

    @message_wrapper
    def send_notify(self, message_list, *args, **kwargs):
        """
        Вызов pg_notify

        Алгоритм:
         - изменение статуса отправки для всех записей на "Отправлено"
         - для каждой записи: генерация pg_notify с данными из атрибута "Данные сообщения" (data)

        :param message_list: список записей из сущности "Сообщения", для которых необходимо сгенерировать notify
        :return:
        """
        for message in message_list:
            data = json.dumps(message.data).replace("'", "'")
            self.cursor.execute(
                self._notify_query.format(message.get_id.channel_name, data)
            )

    @message_wrapper
    def update_message(self, message_list, *args, **kwargs):
        """
        Обновление статуса отправки
        :param message_list: список записей из сущности "Сообщения"
        :return:
        """
        pass

    @message_wrapper
    def create_command_log(self, message_list, *args, **kwargs):
        """
        Создание структуры команд в сущности "Аудит выполнения команд"
        :param message_list: список записей из сущности "Сообщения"
        :return:
        """
        status_set = TaskStatusModel.objects.get(system_name="set")
        status_progress = TaskStatusModel.objects.get(system_name="progress")
        for message in message_list:
            method_list = message.data.get("method_list", None)
            object_list = message.data.get("object_list", None)
            command_list = list()
            is_parallel = True
            if method_list and object_list:
                for method in method_list:
                    try:
                        command = CommandModel.objects.get(
                            method_id__system_name=method,
                            method_id__module_id=message.send_id,
                            action_id=message.task_log_id.action_id,
                        )
                        is_parallel = is_parallel and command.is_parallel
                        command_list.append(command)
                    except CommandModel.DoesNotExist:
                        pass

            if command_list:
                is_first = True
                for command in command_list:
                    for instance in object_list:
                        command_log = CommandLogModel.objects.create(
                            task_log_id=message.task_log_id,
                            parent_id=message.command_log_id,
                            command_id=command,
                            status_id=status_set,
                        )
                        ObjectToCommandLogModel.objects.create(
                            command_log_id=command_log, object_id=uuid.UUID(instance)
                        )
                        if is_parallel or (not is_parallel and is_first):
                            command_log.status_id = status_progress
                            command_log.save()
                    is_first = False

    @message_wrapper
    def update_command_log(self, message_list, *args, **kwargs):
        """
        Обновление статуса выполнения задачи для родительских операций в сущности «Аудит выполнения команд»
        :param message_list: список записей из сущности "Сообщения"
        :return:
        """
        status_dict = {
            MsgTypeChoice.success.value: TaskStatusModel.objects.get(
                system_name="finish"
            ),
            MsgTypeChoice.error.value: TaskStatusModel.objects.get(system_name="error"),
        }
        for message in message_list:
            message.command_log_id.status_id = status_dict[message.msg_type]
            message.command_log_id.save()

    @message_wrapper
    def update_task_log(self, message_list, *args, **kwargs):
        """
        Обновление статуса выполнения задачи для родительских операций в сущности «Аудит выполнения задач»
        :param message_list: список записей из сущности "Сообщения"
        :return:
        """
        status_dict = {
            MsgTypeChoice.success.value: TaskStatusModel.objects.get(
                system_name="finish"
            ),
            MsgTypeChoice.error.value: TaskStatusModel.objects.get(system_name="error"),
        }
        for message in message_list:
            message.task_log_id.status_id = status_dict[message.msg_type]
            message.task_log_id.save()

    @message_wrapper
    def restart_log(self, message_list, *args, **kwargs):
        """
        Перезапуск задач
        :param message_list: список записей из сущности "Сообщения"
        :return:
        """
        send_list = list()
        for message in message_list:
            if message.send_id not in send_list and not message.send_id.status:
                send_list.append(message.send_id)
                message.send_id.status = True
                message.send_id.save()
        # send_list = ModuleModel.objects.filter(get_message_list__in=message_list).distinct()
        method_list = MethodModuleModel.objects.filter(
            module_id__in=send_list, action_list__isnull=False
        ).distinct()
        if method_list:
            task_log_list = TaskLogModel.objects.filter(
                status_id__system_name="progress",
                action_id__method_id__in=method_list,
                command_log_list__isnull=True,
            ).distinct()
            self.create_message(task_log_list, is_restart=True)

        method_list = MethodModuleModel.objects.filter(
            module_id__in=send_list, command_list__isnull=False
        ).distinct()
        if method_list:
            command_log_list = CommandLogModel.objects.filter(
                status_id__system_name="progress",
                command_id__method_id__in=method_list,
                command_log_list__isnull=True,
            ).distinct()
            self.create_message(command_log_list, is_command=True, is_restart=True)

    def period_task(self):
        """
        Периодическая задача (открытый метод)

        Открытый метод в базовом классе вызывается в основном потоке,
        поэтому метод меняет время последнего вызова периодической задачи
        и добавляет периодическую задачу в очередь на выполнение

        :return:
        """
        self.ldt = datetime.now()
        self.pool_task.add_task(self._period_task)

    def _period_task(self):
        """
        Периодическая задача
        :return:
        """
        module_list = ModuleModel.objects.all().exclude(s_id=self.module.s_id)
        post_data = {
            "send_id": self.module,
            "date_created": datetime.now(),
            "status": None,
            "msg_type": MsgTypeChoice.connect.value,
            "parent_msg_id": None,
            "task_log_id": None,
        }
        for module in module_list:
            is_need_connect = True
            if module.status:
                # Если есть запрос на подключение без ответов
                # (то есть прошло period_time минут с последнего запуска периодической задачи),
                # то сообщение необходимо отправить снова
                message_list = MessageModel.objects.filter(
                    get_id=module,
                    send_id=self.module,
                    msg_type=MsgTypeChoice.connect.value,
                    child_list__isnull=True,
                )
                if message_list:
                    module.status = False
                    module.save()
                    # TODO возможно тут сделать команду на перезапуск службы и тогда снова коннект отправлять не надо
                else:
                    # Если есть ответные сообщения о подключении, то проверяем, как давно он был отправлен
                    # Если давно (то есть прошло period_time времени), то сообщение отправлем снова
                    # Нужно для того, чтобы проверять, что службы работают
                    message_list = MessageModel.objects.filter(
                        get_id=self.module,
                        send_id=module,
                        msg_type=MsgTypeChoice.connect.value,
                    )
                    if message_list:
                        last_answer = message_list.order_by("date_created").last()
                        if (
                            last_answer
                            and (last_answer.date_created - datetime.now()).seconds
                            < PERIOD_TIME * 60
                        ):
                            is_need_connect = False

            if is_need_connect:
                s_id = uuid.uuid4()
                post_data["s_id"] = s_id
                post_data["get_id"] = module
                post_data["data"] = {
                    "task_id": str(s_id),
                    "msg_type": MsgTypeChoice.connect.value,
                }
                MessageModel.objects.create(**post_data)

    def check_is_period(self) -> bool:
        """
        Проверка на запуск периодической задачи

        Алгоритм:
         - если время посленего запуска периодической задачи пустое:
            - запускаются поиски изменений для каждого канала
            - возвращает False
         - иначе:
            - проверка по времени на необходимость поиска изменений в соответствующих сущностях
            - запуск соответствующих методов при необходимости
            - проверка по времени на необходимость запуска периодической задачи
            - если необходимо, то возвращает True, иначе False
        :return:
        """
        if not self.ldt:
            self.ldt = datetime.now()
            self.refresh_main_task_log()
            self.refresh_message()
            self.refresh_task_log()
            self.refresh_command_log()
        else:
            for key in self._key_func.keys():
                if self.notify_list[key].is_need_add_task_by_time():
                    refresh_func = getattr(self, self._key_func[key].name)
                    refresh_func()
            if (datetime.now() - self.ldt).seconds >= PERIOD_TIME * 60:
                return True
        return False


class NotifyCount(object):
    _ldt = None
    _count = None
    _max_count = None

    def __init__(self, max_count: int, wait_time: int):
        """
        :param max_count: количество подряд идущих notify
        :param wait_time: время в секундах, через которое запустить проверку таблицы
        """
        self._count = 0
        self._max_count = max_count
        self._wait_time = wait_time

    def is_need_add_task(self) -> bool:
        """
        Если время пустое - пришла первая нотифайка - инициализируем время только для первой натифайки,
        чтобы разницу во времени считать с первой
        Если времени не меньше wait_time секунд или количество сообщений пришло не меньше max_count,
        то обнуляем все и возвращаем True -> следует добавить в очередь задачу для данного канала
        Иначе инкрементируем на единицу количество пришедших notify и возвращаем False -> ожидаем
        :return:
        """
        self._count += 1
        if not self._ldt:
            self._ldt = datetime.now()
        elif (
            datetime.now() - self._ldt
        ).seconds >= self._wait_time or self._count >= self._max_count:
            self._ldt = None
            self._count = 0
            return True
        return False

    def is_need_add_task_by_time(self):
        if self._ldt and (datetime.now() - self._ldt).seconds >= self._wait_time:
            self._ldt = None
            self._count = 0
            return True
        return False

    @property
    def ldt(self):
        return self._ldt

    @property
    def wait_time(self):
        return self._wait_time

    # @property
    # def count(self):
    #     return self._count


if __name__ == "__main__":
    task_svc = TaskSVC(1)
    task_svc.run()
