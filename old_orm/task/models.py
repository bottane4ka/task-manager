# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from uuid import uuid4
from django.contrib.postgres.fields import JSONField


class TemplateTaskModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    parent_id = models.UUIDField(db_column='parent_id', null=True, blank=True, verbose_name='Ссылка на родительскую запись')
    name = models.TextField(db_column='name', null=True, blank=True, verbose_name='Наименование')
    sort_field = models.IntegerField(db_column='sort_field', null=True, blank=True, verbose_name='Поле для сортировки')

    class Meta:
        managed = False
        db_table = 'classifier\".\"template_task'
        verbose_name = 'Базовые задачи'


class TaskModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    name = models.TextField(db_column='name', null=True, blank=True, verbose_name='Наименование')

    class Meta:
        managed = False
        db_table = 'manager\".\"task'
        verbose_name = 'Задачи'


class ActionModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    task_id = models.ForeignKey('task.TaskModel', db_column='task_id', on_delete=models.CASCADE, null=True, blank=True, related_name='action_list', verbose_name='Задача')
    method_id = models.ForeignKey('task.MethodModuleModel', db_column='method_id', on_delete=models.CASCADE, null=True, blank=True, related_name='action_list', verbose_name='Метод')
    action_type_id = models.ForeignKey('classifier.ActionTypeModel', db_column='action_type_id', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Тип операции')
    name = models.TextField(db_column='name', null=True, blank=True, verbose_name='Наименование')
    number = models.IntegerField(db_column='number', null=True, blank=True, verbose_name='Порядковый номер')

    class Meta:
        managed = False
        db_table = 'manager\".\"action'
        verbose_name = 'Операция'


class CommandModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    action_id = models.ForeignKey('task.ActionModel', db_column='action_id', on_delete=models.CASCADE, null=True, blank=True, related_name='command_list', verbose_name='Операция')
    method_id = models.ForeignKey('task.MethodModuleModel', db_column='method_id', on_delete=models.CASCADE, null=True, blank=True, related_name='command_list', verbose_name='Метод')
    parent_id = models.ForeignKey('task.CommandModel', db_column='parent_id', on_delete=models.CASCADE, null=True, blank=True, related_name='command_list', verbose_name='Родительская команда')
    name = models.TextField(db_column='name', null=True, blank=True, verbose_name='Наименование')
    is_parallel = models.BooleanField(db_column='is_parallel', default=False, blank=True, verbose_name='Признак параллельности')
    number = models.IntegerField(db_column='number', null=True, blank=True, verbose_name='Порядковый номер')

    class Meta:
        managed = False
        db_table = 'manager\".\"command'
        verbose_name = 'Команды'


class TaskSequenceModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    template_task_id = models.ForeignKey('task.TemplateTaskModel', db_column='template_task_id', on_delete=models.CASCADE, null=True, blank=True, related_name='task_sequence_list', verbose_name='Базовая задача')
    task_id = models.ForeignKey('task.TaskModel', db_column='task_id', on_delete=models.CASCADE, null=True, blank=True, related_name='task_sequence_list', verbose_name='Задача')
    number = models.IntegerField(db_column='number', null=True, blank=True, verbose_name='Порядковый номер')

    class Meta:
        managed = False
        db_table = 'manager\".\"task_sequence'
        verbose_name = 'Последовательность задач'


class MainTaskLogModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    template_task_id = models.ForeignKey('task.TemplateTaskModel', db_column='template_task_id', on_delete=models.CASCADE, null=True, blank=True, related_name='main_task_log_list', verbose_name='Базовая задача')
    status_id = models.ForeignKey('classifier.StatusTaskModel', db_column='status_id', on_delete=models.CASCADE, null=True, blank=True, related_name='main_task_log_list', verbose_name='Статус выполнения задачи')
    base = models.TextField(db_column='base', null=True, blank=True, verbose_name='Основание')
    add_task_date = models.DateTimeField(db_column='add_task_date', null=True, blank=True, verbose_name='Дата постановки задачи')
    exec_task_date = models.DateTimeField(db_column='exec_task_date', null=True, blank=True, verbose_name='Дата запуска задачи')
    end_task_date = models.DateTimeField(db_column='end_task_date', null=True, blank=True, verbose_name='Дата выполнения задачи')

    class Meta:
        managed = False
        db_table = 'manager\".\"main_task_log'
        verbose_name = 'Аудит выполнения задач'


class TaskLogModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    main_task_log_id = models.ForeignKey('task.MainTaskLogModel', db_column='main_task_log_id', on_delete=models.CASCADE, null=True, blank=True, related_name='task_log_list', verbose_name='Аудит выполнения задач')
    action_id = models.ForeignKey('task.ActionModel', db_column='action_id', on_delete=models.CASCADE, null=True, blank=True, related_name='task_log_list', verbose_name='Операция')
    status_id = models.ForeignKey('classifier.StatusTaskModel', db_column='status_id', on_delete=models.CASCADE, null=True, blank=True, related_name='task_log_list', verbose_name='Статус выполнения задачи')

    class Meta:
        managed = False
        db_table = 'manager\".\"task_log'
        verbose_name = 'Аудит выполнения задач'


class CommandLogModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    task_log_id = models.ForeignKey('task.TaskLogModel', db_column='task_log_id', on_delete=models.CASCADE, null=True, blank=True, related_name='command_log_list', verbose_name='Аудит выполнения задач')
    parent_id = models.ForeignKey('task.CommandLogModel', db_column='parent_id', on_delete=models.CASCADE, null=True, blank=True, related_name='command_log_list', verbose_name='Родительская команда')
    command_id = models.ForeignKey('task.CommandModel', db_column='command_id', on_delete=models.CASCADE, null=True, blank=True, related_name='command_log_list', verbose_name='Команда')
    status_id = models.ForeignKey('classifier.StatusTaskModel', db_column='status_id', on_delete=models.CASCADE, null=True, blank=True, related_name='command_log_list', verbose_name='Статус выполнения задачи')

    class Meta:
        managed = False
        db_table = 'manager\".\"command_log'
        verbose_name = 'Аудит выполнения команд'


class MessageModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    task_log_id = models.ForeignKey('task.TaskLogModel', db_column='task_log_id', on_delete=models.CASCADE, null=True, blank=True, related_name='message_list', verbose_name='Аудит выполнения задач')
    command_log_id = models.ForeignKey('task.CommandLogModel', db_column='command_log_id', on_delete=models.CASCADE, null=True, blank=True, related_name='message_list', verbose_name='Аудит выполнения команд')
    parent_msg_id = models.ForeignKey('task.MessageModel', db_column='parent_msg_id', on_delete=models.CASCADE, null=True, blank=True, related_name='child_list', verbose_name='Родительское сообщение')
    send_id = models.ForeignKey('task.ModuleModel', db_column='send_id', on_delete=models.CASCADE, null=True, blank=True, related_name='send_message_list', verbose_name='Отправитель')
    get_id = models.ForeignKey('task.ModuleModel', db_column='get_id', on_delete=models.CASCADE, null=True, blank=True, related_name='get_message_list', verbose_name='Получатель')
    data = JSONField(db_column='data', null=True, blank=True, verbose_name='Данные сообщения')
    msg_type = models.TextField(db_column='msg_type', choices=[(tag, tag.value) for tag in MsgTypeChoice], null=True, blank=True, verbose_name='Тип сообщения')
    status = models.TextField(db_column='status', choices=[(tag, tag.value) for tag in StatusSendChoice], null=True, blank=True, verbose_name='Статус отправки')
    date_created = models.DateTimeField(db_column='date_created', null=True, blank=True, verbose_name='Дата и время создания')

    class Meta:
        managed = False
        db_table = 'manager\".\"message'
        verbose_name = 'Сообщения'


class ModuleModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    name = models.TextField(db_column='name', null=True, blank=True, verbose_name='Наименование')
    system_name = models.TextField(db_column='system_name', null=True, blank=True, verbose_name='Системное наименование')
    channel_name = models.TextField(db_column='channel_name', null=True, blank=True, verbose_name='Наименование канала')
    status = models.BooleanField(db_column='status', default=False, blank=True, verbose_name='Статус работоспособности')

    class Meta:
        managed = False
        db_table = 'manager\".\"module'
        verbose_name = 'Службы и модули'


class MethodModuleModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    module_id = models.ForeignKey('task.ModuleModel', db_column='module_id', on_delete=models.CASCADE, null=True, blank=True, related_name='method_list', verbose_name='Служба или модуль')
    name = models.TextField(db_column='name', null=True, blank=True, verbose_name='Наименование')
    system_name = models.TextField(db_column='system_name', null=True, blank=True, verbose_name='Системное наименование')

    class Meta:
        managed = False
        db_table = 'manager\".\"method_module'
        verbose_name = 'Методы служб и модулей'


class ObjectToTaskLogModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    task_log_id = models.ForeignKey('task.TaskLogModel', db_column='task_log_id', on_delete=models.CASCADE, null=True, blank=True, related_name='object_to_task_log_list', verbose_name='Задача')
    object_id = models.UUIDField(db_column='object_id', null=True, blank=True, verbose_name='Идентификатор объекта')

    class Meta:
        managed = False
        db_table = 'manager\".\"object_to_task_log'
        verbose_name = 'Связь Аудита выполнения задач с записью объекта'


class ObjectToCommandLogModel(models.Model):

    s_id = models.UUIDField(db_column='s_id', primary_key=True, default=uuid4, editable=False, unique=True, blank=True, verbose_name='Идентификатор')
    command_log_id = models.ForeignKey('task.CommandLogModel', db_column='command_log_id', on_delete=models.CASCADE, null=True, blank=True, related_name='object_to_command_log_list', verbose_name='Команда')
    object_id = models.UUIDField(db_column='object_id', null=True, blank=True, verbose_name='Идентификатор объекта')

    class Meta:
        managed = False
        db_table = 'manager\".\"object_to_command_log'
        verbose_name = 'Связь Аудита выполнения команд с записью объекта'
