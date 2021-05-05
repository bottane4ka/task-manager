# -*- coding: utf-8 -*-
from enum import Enum
from uuid import uuid4
from datetime import datetime

from django.db import models
from django.contrib.postgres.fields import JSONField


class StatusSendChoice(Enum):
    sent = "Отправлено"
    recd = "Получено"
    ok = "Обработано"


class MsgTypeChoice(Enum):
    connect = "Подключение"
    task = "Задача"
    info = "Информация"
    success = "Выполнено"
    error = "Ошибка"
    warning = "Внимание"


class ActionModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    task = models.ForeignKey(
        "manager.TaskModel",
        db_column="task_id",
        on_delete=models.CASCADE,
        related_name="action_list",
        verbose_name="Задача",
    )
    method = models.ForeignKey(
        "manager.MethodModuleModel",
        db_column="method_id",
        on_delete=models.CASCADE,
        related_name="action_list",
        verbose_name="Метод",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")
    number = models.IntegerField(
        db_column="number", default=1, blank=True, verbose_name="Порядковый номер"
    )

    class Meta:
        db_table = "action"
        db_tablespace = "manager"
        verbose_name = "Действие"
        verbose_name_plural = "Действия"


class BaseTaskModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")

    class Meta:
        db_table = "base_task"
        db_tablespace = "manager"
        verbose_name = "Базовая задача"
        verbose_name_plural = "Базовые задачи"


class CommandModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    action = models.ForeignKey(
        "manager.ActionModel",
        db_column="action_id",
        on_delete=models.CASCADE,
        related_name="command_list",
        verbose_name="Операция",
    )
    method = models.ForeignKey(
        "manager.MethodModuleModel",
        db_column="method_id",
        on_delete=models.CASCADE,
        related_name="command_list",
        verbose_name="Метод",
    )
    parent = models.ForeignKey(
        "manager.CommandModel",
        db_column="parent_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="command_list",
        verbose_name="Родительская команда",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")
    is_parallel = models.BooleanField(
        db_column="is_parallel",
        default=False,
        blank=True,
        verbose_name="Признак параллельности",
    )
    number = models.IntegerField(
        db_column="number", default=1, blank=True, verbose_name="Порядковый номер"
    )

    class Meta:
        db_table = "command"
        db_tablespace = "manager"
        verbose_name = "Команда"
        verbose_name_plural = "Команды"


class CommandLogModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    task_log = models.ForeignKey(
        "manager.TaskLogModel",
        db_column="task_log_id",
        on_delete=models.CASCADE,
        related_name="command_log_list",
        verbose_name="Аудит выполнения задач",
    )
    parent = models.ForeignKey(
        "manager.CommandLogModel",
        db_column="parent_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="command_log_list",
        verbose_name="Родительская команда",
    )
    command = models.ForeignKey(
        "manager.CommandModel",
        db_column="command_id",
        on_delete=models.CASCADE,
        related_name="command_log_list",
        verbose_name="Команда",
    )
    status = models.ForeignKey(
        "manager.TaskStatusModel",
        db_column="status_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="command_log_list",
        verbose_name="Статус выполнения задач",
    )

    class Meta:
        db_table = "command_log"
        db_tablespace = "manager"
        verbose_name = "Аудит выполнения команды"
        verbose_name_plural = "Аудит выполнения команд"


class BaseTaskLogModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    base_task = models.ForeignKey(
        "manager.BaseTaskModel",
        db_column="base_task_id",
        on_delete=models.CASCADE,
        related_name="main_task_log_list",
        verbose_name="Базовая задача",
    )
    status = models.ForeignKey(
        "manager.TaskStatusModel",
        db_column="status_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="main_task_log_list",
        verbose_name="Статус выполнения задачи",
    )
    add_task_date = models.DateTimeField(
        db_column="add_task_date",
        default=datetime.now,
        blank=True,
        verbose_name="Дата постановки базовой задачи",
    )
    exec_task_date = models.DateTimeField(
        db_column="exec_task_date",
        null=True,
        blank=True,
        verbose_name="Дата начала выполнения задачи",
    )
    end_task_date = models.DateTimeField(
        db_column="end_task_date",
        null=True,
        blank=True,
        verbose_name="Дата окончания выполнения задачи",
    )

    class Meta:
        db_table = "base_task_log"
        db_tablespace = "manager"
        verbose_name = "Аудит выполнения базовой задачи"
        verbose_name_plural = "Аудит выполнения базовых задач"


class MessageModel(models.Model):

    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    task_log = models.ForeignKey(
        "manager.TaskLogModel",
        db_column="task_log_id",
        on_delete=models.CASCADE,
        related_name="message_list",
        verbose_name="Аудит выполнения задач",
    )
    command_log = models.ForeignKey(
        "manager.CommandLogModel",
        db_column="command_log_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="message_list",
        verbose_name="Аудит выполнения команд",
    )
    parent_msg = models.ForeignKey(
        "manager.MessageModel",
        db_column="parent_msg_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_list",
        verbose_name="Родительское сообщение",
    )
    sender = models.ForeignKey(
        "manager.ModuleModel",
        db_column="sender_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="send_message_list",
        verbose_name="Отправитель",
    )
    recipient = models.ForeignKey(
        "manager.ModuleModel",
        db_column="recipient_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recipient_message_list",
        verbose_name="Получатель",
    )
    data = JSONField(
        db_column="data", null=True, blank=True, verbose_name="Данные сообщения"
    )
    msg_type = models.TextField(
        db_column="msg_type",
        choices=[(tag, tag.value) for tag in MsgTypeChoice],
        default=MsgTypeChoice.connect.value,
        verbose_name="Тип сообщения",
    )
    status = models.TextField(
        db_column="status",
        choices=[(tag, tag.value) for tag in StatusSendChoice],
        null=True,
        blank=True,
        verbose_name="Статус отправки",
    )
    date_created = models.DateTimeField(
        db_column="date_created",
        default=datetime.now,
        blank=True,
        verbose_name="Дата и время создания",
    )

    class Meta:
        db_table = "message"
        db_tablespace = "manager"
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class MethodModuleModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    module = models.ForeignKey(
        "manager.ModuleModel",
        db_column="module_id",
        on_delete=models.CASCADE,
        related_name="method_list",
        verbose_name="Служба",
    )
    name = models.TextField(
        db_column="name", null=True, blank=True, verbose_name="Наименование"
    )
    system_name = models.TextField(
        db_column="system_name", verbose_name="Системное наименование"
    )

    class Meta:
        db_table = "method_module"
        db_tablespace = "manager"
        verbose_name = "Метод службы"
        verbose_name_plural = "Методы служб"


class ModuleModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    name = models.TextField(
        db_column="name", null=True, blank=True, verbose_name="Наименование"
    )
    system_name = models.TextField(
        db_column="system_name", verbose_name="Системное наименование"
    )
    channel_name = models.TextField(
        db_column="channel_name", unique=True, verbose_name="Наименование канала"
    )
    status = models.BooleanField(
        db_column="status",
        default=False,
        blank=True,
        verbose_name="Статус работоспособности",
    )

    class Meta:
        db_table = "module"
        db_tablespace = "manager"
        verbose_name = "Служба"
        verbose_name_plural = "Службы"


class ObjectToCommandLogModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    command_log = models.ForeignKey(
        "manager.CommandLogModel",
        db_column="command_log_id",
        on_delete=models.CASCADE,
        related_name="object_to_command_log_list",
        verbose_name="Команда",
    )
    related_object = models.UUIDField(
        db_column="object_id", verbose_name="Идентификатор объекта"
    )

    class Meta:
        db_table = "object_to_command_log"
        db_tablespace = "manager"
        verbose_name = "Аудит выполнения команды - Объект"
        verbose_name_plural = "Аудит выполнения команд - Объекты"


class ObjectToTaskLogModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    task_log = models.ForeignKey(
        "manager.TaskLogModel",
        db_column="task_log_id",
        on_delete=models.CASCADE,
        related_name="object_to_task_log_list",
        verbose_name="Аудит выполнения задач",
    )
    related_object = models.UUIDField(
        db_column="object_id", verbose_name="Идентификатор объекта"
    )

    class Meta:
        db_table = "object_to_task_log"
        db_tablespace = "manager"
        verbose_name = "Аудит выполнения задачи - Объект"
        verbose_name_plural = "Аудит выполнения задач - Объекты"


class TaskModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")

    class Meta:
        db_table = "task"
        db_tablespace = "manager"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class TaskLogModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    main_task_log = models.ForeignKey(
        "manager.BaseTaskLogModel",
        db_column="main_task_log_id",
        on_delete=models.CASCADE,
        related_name="task_log_list",
        verbose_name="Аудит выполнения базовых задач",
    )
    action = models.ForeignKey(
        "manager.ActionModel",
        db_column="action_id",
        on_delete=models.CASCADE,
        related_name="task_log_list",
        verbose_name="Операция",
    )
    status = models.ForeignKey(
        "manager.TaskStatusModel",
        db_column="status_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="task_log_list",
        verbose_name="Статус выполнения задач",
    )

    class Meta:
        db_table = "task_log"
        db_tablespace = "manager"
        verbose_name = "Аудит выполнения задачи"
        verbose_name_plural = "Аудит выполнения задач"


class TaskSequenceModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    base_task = models.ForeignKey(
        "manager.BaseTaskModel",
        db_column="base_task_id",
        on_delete=models.CASCADE,
        related_name="task_sequence_list",
        verbose_name="Базовая задача",
    )
    task = models.ForeignKey(
        "manager.TaskModel",
        db_column="task_id",
        on_delete=models.CASCADE,
        related_name="task_sequence_list",
        verbose_name="Задача",
    )
    number = models.IntegerField(
        db_column="number", default=1, blank=True, verbose_name="Порядковый номер"
    )

    class Meta:
        db_table = "task_sequence"
        db_tablespace = "manager"
        verbose_name = "Последовательность задач"
        verbose_name_plural = "Последовательности задач"


class TaskStatusModel(models.Model):
    id = models.UUIDField(
        db_column="s_id",
        primary_key=True,
        default=uuid4,
        editable=False,
        unique=True,
        blank=True,
        verbose_name="Идентификатор",
    )
    name = models.TextField(db_column="name", verbose_name="Наименование")
    system_name = models.TextField(
        db_column="system_name", verbose_name="Системное наименование"
    )

    class Meta:
        db_table = "task_status"
        db_tablespace = "manager"
        verbose_name = "Статус выполнения задачи"
        verbose_name_plural = "Статусы выполнения задачи"
