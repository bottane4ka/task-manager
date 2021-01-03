# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, backref
from utils.status_type import StatusSendChoice, MsgTypeChoice
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ActionModel(Base):

    __tablename__ = "action"
    __table_args__ = {
        "schema": "manager",
        "comment": "Операции"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_id = Column("task_id", UUID(as_uuid=True), ForeignKey("manager.task.s_id"), nullable=False, info={"verbose_name": "Задача"})
    method_id = Column("method_id", UUID(as_uuid=True), ForeignKey("manager.method_module.s_id"), nullable=False, info={"verbose_name": "Метод службы"})
    name = Column("name", Text, nullable=False, info={"verbose_name": "Наименование"})
    number = Column("number", Integer, default=1, info={"verbose_name": "Порядковый номер"})

    task = relationship("TaskModel", backref="method_list")
    method = relationship("MethodModuleModel", backref="method_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ActionModel {self.s_id}>"


class BaseTaskModel(Base):

    __tablename__ = "base_task"
    __table_args__ = {
        "schema": "manager",
        "comment": "Базовые задачи"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = Column("name", Text, nullable=False, info={"verbose_name": "Наименование"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<BaseTaskModel {self.s_id}>"


class CommandModel(Base):

    __tablename__ = "command"
    __table_args__ = {
        "schema": "manager",
        "comment": "Команды"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    action_id = Column("action_id", UUID(as_uuid=True), ForeignKey("manager.action.s_id"), nullable=False, info={"verbose_name": "Действие"})
    method_id = Column("method_id", UUID(as_uuid=True), ForeignKey("manager.method_module.s_id"), nullable=False, info={"verbose_name": "Метод службы"})
    parent_id = Column("parent_id", UUID(as_uuid=True), ForeignKey("manager.command.s_id"), nullable=True, info={"verbose_name": "Родительская команда"})
    name = Column("name", Text, nullable=False, info={"verbose_name": "Наименование"})
    is_parallel = Column("is_parallel", Boolean, default=False, info={"verbose_name": "Признак параллельности"})
    number = Column("number", Integer, default=1, info={"verbose_name": "Порядковый номер"})

    action = relationship("ActionModel", backref="command_list")
    method = relationship("MethodModuleModel", backref="command_list")
    parent = relationship("CommandModel", backref=backref("child_list", remote_side=s_id))

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<CommandModel {self.s_id}>"


class CommandLogModel(Base):

    __tablename__ = "command_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения команд"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = Column("task_log_id", UUID(as_uuid=True), ForeignKey("manager.task_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения задач"})
    parent_id = Column("parent_id", UUID(as_uuid=True), ForeignKey("manager.command_log.s_id"), nullable=True, info={"verbose_name": "Родительская выполняемая команда"})
    command_id = Column("command_id", UUID(as_uuid=True), ForeignKey("manager.command.s_id"), nullable=False, info={"verbose_name": "Команда"})
    status_id = Column("status_id", UUID(as_uuid=True), ForeignKey("manager.task_completion_status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})

    task_log = relationship("TaskLogModel", backref="command_log_list")
    parent = relationship("CommandLogModel", backref=backref("child_list", remote_side=s_id))
    command = relationship("CommandModel", backref="command_log_list")
    status = relationship("TaskStatusModel", backref="command_log_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<CommandLogModel {self.s_id}>"


class MainTaskLogModel(Base):

    __tablename__ = "main_task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения базовых задач"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    base_task_id = Column("task_log_id", UUID(as_uuid=True), ForeignKey("manager.base_task.s_id"), nullable=False, info={"verbose_name": "Базовая задача"})
    status_id = Column("status_id", UUID(as_uuid=True), ForeignKey("manager.task_completion_status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})
    add_task_date = Column("add_task_date", DateTime, default=datetime.now, info={"verbose_name": "Дата и время постановки задачи"})
    exec_task_date = Column("exec_task_date", DateTime, nullable=True, info={"verbose_name": "Дата и время начала выполнения задачи"})
    end_task_date = Column("end_task_date", DateTime, nullable=True, info={"verbose_name": "Дата и время окончания выполнения задачи"})

    base_task = relationship("BaseTaskModel", backref="main_task_log_list")
    status = relationship("TaskStatusModel", backref="main_task_log_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<MainTaskLogModel {self.s_id}>"


class MessageModel(Base):

    __tablename__ = "message"
    __table_args__ = {
        "schema": "manager",
        "comment": "Сообщения"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = Column("task_log_id", UUID(as_uuid=True), ForeignKey("manager.task_log.s_id"), nullable=True, info={"verbose_name": "Аудит выполнения задач"})
    command_log_id = Column("command_log_id", UUID(as_uuid=True), ForeignKey("manager.command_log.s_id"), nullable=True, info={"verbose_name": "Аудит выполнения команд"})
    parent_msg_id = Column("parent_msg_id", UUID(as_uuid=True), ForeignKey("manager.message.s_id"), nullable=True, info={"verbose_name": "Родительское сообщение"})
    send_id = Column("send_id", UUID(as_uuid=True), ForeignKey("manager.module.s_id"), nullable=True, info={"verbose_name": "Отправитель"})
    get_id = Column("get_id", UUID(as_uuid=True), ForeignKey("manager.module.s_id"), nullable=False, info={"verbose_name": "Получатель"})
    data = Column("data", JSONB, nullable=True, info={"verbose_name": "Данные"})
    msg_type = Column("name", Enum(MsgTypeChoice), default=MsgTypeChoice.connect.value, info={"verbose_name": "Тип сообщения"})
    status = Column("status", Enum(StatusSendChoice), default=StatusSendChoice.sent.value, info={"verbose_name": "Статус отправки"})
    date_created = Column("date_created", DateTime, default=datetime.now, info={"verbose_name": "Дата создания"})

    task_log = relationship("TaskLogModel", backref="message_list")
    parent_msg = relationship("MessageModel", backref=backref("child_list", remote_side=s_id))
    command_log = relationship("CommandLogModel", backref="message_list")
    get = relationship("ModuleModel", foreign_keys=[get_id], backref="get_message_list")
    send = relationship("ModuleModel", foreign_keys=[send_id], backref="send_message_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<MessageModel {self.s_id}>"


class MethodModuleModel(Base):

    __tablename__ = "method_module"
    __table_args__ = {
        "schema": "manager",
        "comment": "Методы функциональных служб"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    module_id = Column("module_id", UUID(as_uuid=True), ForeignKey("manager.module.s_id"), nullable=False, info={"verbose_name": "Служба"})
    name = Column("name", Text, nullable=False, info={"verbose_name": "Наименование"})
    system_name = Column("system_name", Text, nullable=False, info={"verbose_name": "Системное наименование"})

    module = relationship("ModuleModel", backref="method_module_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<MethodModuleModel {self.s_id}>"


class ModuleModel(Base):

    __tablename__ = "module"
    __table_args__ = {
        "schema": "manager",
        "comment": "Службы"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = Column("name", Text, nullable=False, info={"verbose_name": "Наименование"})
    system_name = Column("system_name", Text, nullable=False, info={"verbose_name": "Системное наименование"})
    channel_name = Column("channel_name", Text, nullable=False, info={"verbose_name": "Наименование канала"})
    status = Column("status", Boolean, default=False, info={"verbose_name": "Статус работоспособности"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ModuleModel {self.s_id}>"


class ObjectToCommandLogModel(Base):

    __tablename__ = "object_to_command_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Связь Аудита выполнения команд с записью объекта"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    command_log_id = Column("command_log_id", UUID(as_uuid=True), ForeignKey("manager.command_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения команд"})
    object_id = Column("object_id", UUID(as_uuid=True), nullable=False, info={"verbose_name": "Объект"})

    command_log = relationship("CommandLogModel", backref="object_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ObjectToCommandLogModel {self.s_id}>"


class ObjectToTaskLogModel(Base):

    __tablename__ = "object_to_task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Связь Аудита выполнения задачи с записью объекта"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = Column("task_log_id", UUID(as_uuid=True), ForeignKey("manager.task_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения задач"})
    object_id = Column("object_id", UUID(as_uuid=True), nullable=False, info={"verbose_name": "Объект"})

    task_log = relationship("TaskLogModel", backref="object_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<ObjectToTaskLogModel {self.s_id}>"


class TaskModel(Base):

    __tablename__ = "task"
    __table_args__ = {
        "schema": "manager",
        "comment": "Задачи"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = Column("name", Text, nullable=False, info={"verbose_name": "Наименование"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskModel {self.s_id}>"


class TaskLogModel(Base):

    __tablename__ = "task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения задач"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    main_task_log_id = Column("main_task_log_id", UUID(as_uuid=True), ForeignKey("manager.main_task_log.s_id"), nullable=False, info={"verbose_name": ""})
    action_id = Column("action_id", UUID(as_uuid=True), ForeignKey("manager.action.s_id"), nullable=False, info={"verbose_name": "Операция"})
    status_id = Column("status_id", UUID(as_uuid=True), ForeignKey("manager.task_completion_status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})

    main_task_log = relationship("MainTaskLogModel", backref="task_log_list")
    action = relationship("ActionModel", backref="task_log_list")
    status = relationship("TaskStatusModel", backref="task_log_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskLogModel {self.s_id}>"


class TaskSequenceModel(Base):

    __tablename__ = "task_sequence"
    __table_args__ = {
        "schema": "manager",
        "comment": "Последовательность задач"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    base_task_id = Column("base_task_id", UUID(as_uuid=True), ForeignKey("manager.base_task.s_id"), nullable=False, info={"verbose_name": "Базовая задача"})
    task_id = Column("task_id", UUID(as_uuid=True), ForeignKey("manager.task.s_id"), nullable=False, info={"verbose_name": "Задача"})
    number = Column("number", Integer, default=1, info={"verbose_name": "Порядковый номер"})

    base_task = relationship("BaseTaskModel", backref="task_sequence_list")
    task = relationship("TaskModel", backref="task_sequence_list")

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskSequenceModel {self.s_id}>"


class TaskStatusModel(Base):

    __tablename__ = "task_completion_status"
    __table_args__ = {
        "schema": "manager",
        "comment": "Статус выполнения задачи"
    }

    s_id = Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    name = Column("name", Text, nullable=False, info={"verbose_name": "Наименование"})
    system_name = Column("system_name", Text, nullable=False, info={"verbose_name": "Системное наименование"})

    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __repr__(self):
        return f"<TaskStatusModel {self.s_id}>"

