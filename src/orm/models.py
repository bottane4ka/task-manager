# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import datetime
from orm.manage import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from utils.status_type import StatusSendChoice, MsgTypeChoice


class ActionModel(db.Model):

    __tablename__ = "action"
    __table_args__ = {
        "schema": "manager",
        "comment": "Операции"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_id = db.Column("task_id", UUID(as_uuid=True), db.ForeignKey("manager.task.s_id"), nullable=False, info={"verbose_name": "Задача"})
    method_id = db.Column("method_id", UUID(as_uuid=True), db.ForeignKey("manager.method_module.s_id"), nullable=False, info={"verbose_name": "Метод службы"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    number = db.Column("number", db.Integer, default=1, info={"verbose_name": "Порядковый номер"})

    method = db.relationship("MethodModuleModel", backref="method_list")
    # task_log_list = db.relationship("TaskLogModel", backref="action", order_by="TaskLogModel.s_id")
    # command_list = db.relationship("CommandModel", backref="action", order_by="CommandModel.number")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ActionModel {self.s_id}>"


class BaseTaskModel(db.Model):

    __tablename__ = "base_task"
    __table_args__ = {
        "schema": "manager",
        "comment": "Базовые задачи"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})

    base_task_log_list = db.relationship("MainTaskLogModel", backref="base_task", order_by="MainTaskLogModel.add_task_date")
    task_sequence_list = db.relationship("TaskSequenceModel", backref="base_task", order_by="TaskSequenceModel.s_id")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<BaseTaskModel {self.s_id}>"


class CommandModel(db.Model):

    __tablename__ = "command"
    __table_args__ = {
        "schema": "manager",
        "comment": "Команды"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    action_id = db.Column("action_id", UUID(as_uuid=True), db.ForeignKey("manager.action.s_id"), nullable=False, info={"verbose_name": "Действие"})
    method_id = db.Column("method_id", UUID(as_uuid=True), db.ForeignKey("manager.method.s_id"), nullable=False, info={"verbose_name": "Метод службы"})
    parent_id = db.Column("parent_id", UUID(as_uuid=True), db.ForeignKey("manager.parent.s_id"), nullable=True, info={"verbose_name": "Родительская команда"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    is_parallel = db.Column("is_parallel", db.Boolean, default=False, info={"verbose_name": "Признак параллельности"})
    number = db.Column("number", db.Integer, default=1, info={"verbose_name": "Порядковый номер"})

    command_log_list = db.relationship("CommandLogModel", backref="command", order_by="CommandLogModel.s_id")
    # child_list = db.relationship("CommandModel", backref="parent", order_by="CommandLogModel.s_id")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<CommandModel {self.s_id}>"


class CommandLogModel(db.Model):

    __tablename__ = "command_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения команд"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("manager.task_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения задач"})
    parent_id = db.Column("parent_id", UUID(as_uuid=True), db.ForeignKey("manager.parent.s_id"), nullable=True, info={"verbose_name": "Родительская выполняемая команда"})
    command_id = db.Column("command_id", UUID(as_uuid=True), db.ForeignKey("manager.command.s_id"), nullable=False, info={"verbose_name": "Команда"})
    status_id = db.Column("status_id", UUID(as_uuid=True), db.ForeignKey("manager.status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})

    message_list = db.relationship("MessageModel", backref="command_log", order_by="MessageModel.date_created")
    # child_list = db.relationship("CommandLogModel", backref="parent", order_by="CommandLogModel.s_id")
    object_list = db.relationship("ObjectToCommandLogModel", backref="command_log", order_by="ObjectToCommandLogModel.s_id")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<CommandLogModel {self.s_id}>"


class MainTaskLogModel(db.Model):

    __tablename__ = "main_task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения базовых задач"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    base_task_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("manager.base_task.s_id"), nullable=False, info={"verbose_name": "Базовая задача"})
    status_id = db.Column("status_id", UUID(as_uuid=True), db.ForeignKey("manager.task_completion_status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})
    add_task_date = db.Column("add_task_date", db.DateTime, default=datetime.now, info={"verbose_name": "Дата и время постановки задачи"})
    exec_task_date = db.Column("exec_task_date", db.DateTime, nullable=True, info={"verbose_name": "Дата и время начала выполнения задачи"})
    end_task_date = db.Column("end_task_date", db.DateTime, nullable=True, info={"verbose_name": "Дата и время окончания выполнения задачи"})

    task_log_list = db.relationship("TaskLogModel", backref="main_task_log", order_by="TaskLogModel.s_id")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<MainTaskLogModel {self.s_id}>"


class MessageModel(db.Model):

    __tablename__ = "message"
    __table_args__ = {
        "schema": "manager",
        "comment": "Сообщения"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("manager.base_task.s_id"), nullable=True, info={"verbose_name": "Аудит выполнения задач"})
    command_log_id = db.Column("command_log_id", UUID(as_uuid=True), db.ForeignKey("manager.command_log.s_id"), nullable=True, info={"verbose_name": "Аудит выполнения команд"})
    parent_msg_id = db.Column("parent_msg_id", UUID(as_uuid=True), db.ForeignKey("manager.message.s_id"), nullable=True, info={"verbose_name": "Родительское сообщение"})
    send_id = db.Column("send_id", UUID(as_uuid=True), db.ForeignKey("manager.module.s_id"), nullable=True, info={"verbose_name": "Отправитель"})
    get_id = db.Column("get_id", UUID(as_uuid=True), db.ForeignKey("manager.module.s_id"), nullable=False, info={"verbose_name": "Получатель"})
    data = db.Column("data", JSONB, nullable=True, info={"verbose_name": "Данные"})
    msg_type = db.Column("name", db.Enum(MsgTypeChoice), default=MsgTypeChoice.connect.value, info={"verbose_name": "Тип сообщения"})
    status = db.Column("status", db.Enum(StatusSendChoice), default=StatusSendChoice.sent.value, info={"verbose_name": "Статус отправки"})
    date_created = db.Column("date_created", db.DateTime, default=datetime.now, info={"verbose_name": "Дата создания"})

    # child_list = db.relationship("MessageModel", backref="parent_msg", order_by="MessageModel.date_created")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<MessageModel {self.s_id}>"


class MethodModuleModel(db.Model):

    __tablename__ = "method_module"
    __table_args__ = {
        "schema": "manager",
        "comment": "Методы функциональных служб"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    module_id = db.Column("module_id", UUID(as_uuid=True), db.ForeignKey("manager.module.s_id"), nullable=False, info={"verbose_name": "Служба"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    system_name = db.Column("system_name", db.Text, nullable=False, info={"verbose_name": "Системное наименование"})

    # action_list = db.relationship("ActionModel", backref="method", order_by="ActionModel.name")
    # command_list = db.relationship("CommandModel", backref="method", order_by="CommandModel.name")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<MethodModuleModel {self.s_id}>"


class ModuleModel(db.Model):

    __tablename__ = "module"
    __table_args__ = {
        "schema": "manager",
        "comment": "Службы"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    system_name = db.Column("system_name", db.Text, nullable=False, info={"verbose_name": "Системное наименование"})
    channel_name = db.Column("channel_name", db.Text, nullable=False, info={"verbose_name": "Наименование канала"})
    status = db.Column("status", db.Boolean, default=False, info={"verbose_name": "Статус работоспособности"})

    method_list = db.relationship("MethodModuleModel", backref="module", order_by="MethodModuleModel.s_id")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ModuleModel {self.s_id}>"


class ObjectToCommandLogModel(db.Model):

    __tablename__ = "object_to_command_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Связь Аудита выполнения команд с записью объекта"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    command_log_id = db.Column("command_log_id", UUID(as_uuid=True), db.ForeignKey("manager.command_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения команд"})
    object_id = db.Column("object_id", UUID(as_uuid=True), nullable=False, info={"verbose_name": "Объект"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ObjectToCommandLogModel {self.s_id}>"


class ObjectToTaskLogModel(db.Model):

    __tablename__ = "object_to_task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Связь Аудита выполнения задачи с записью объекта"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("manager.task_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения задач"})
    object_id = db.Column("object_id", UUID(as_uuid=True), nullable=False, info={"verbose_name": "Объект"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ObjectToTaskLogModel {self.s_id}>"


class TaskModel(db.Model):

    __tablename__ = "task"
    __table_args__ = {
        "schema": "manager",
        "comment": "Задачи"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})

    action_list = db.relationship("ActionModel", backref="task", order_by="ActionModel.number")
    task_sequence_list = db.relationship("TaskSequenceModel", backref="task", order_by="TaskSequenceModel.s_id")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskModel {self.s_id}>"


class TaskLogModel(db.Model):

    __tablename__ = "task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения задач"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    main_task_log_id = db.Column("main_task_log_id", UUID(as_uuid=True), db.ForeignKey("manager.main_task_log.s_id"), nullable=False, info={"verbose_name": ""})
    action_id = db.Column("action_id", UUID(as_uuid=True), db.ForeignKey("manager.action.s_id"), nullable=False, info={"verbose_name": "Операция"})
    status_id = db.Column("status_id", UUID(as_uuid=True), db.ForeignKey("manager.task_completion_status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})

    action = db.relationship("ActionModel", backref="task_log_list")
    command_log = db.relationship("CommandLogModel", backref="task_log", order_by="CommandLogModel.s_id")
    object_list = db.relationship("ObjectToTaskLogModel", backref="task_log", order_by="ObjectToTaskLogModel.s_id")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskLogModel {self.s_id}>"


class TaskSequenceModel(db.Model):

    __tablename__ = "task_sequence"
    __table_args__ = {
        "schema": "manager",
        "comment": "Последовательность задач"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    base_task_id = db.Column("base_task_id", UUID(as_uuid=True), db.ForeignKey("manager.base_task.s_id"), nullable=False, info={"verbose_name": "Базовая задача"})
    task_id = db.Column("task_id", UUID(as_uuid=True), db.ForeignKey("manager.task.s_id"), nullable=False, info={"verbose_name": "Задача"})
    number = db.Column("number", db.Integer, default=1, info={"verbose_name": "Порядковый номер"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskSequenceModel {self.s_id}>"


class TaskStatusModel(db.Model):

    __tablename__ = "task_completion_status"
    __table_args__ = {
        "schema": "manager",
        "comment": "Статус выполнения задачи"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    system_name = db.Column("system_name", db.Text, nullable=False, info={"verbose_name": "Системное наименование"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskStatusModel {self.s_id}>"

