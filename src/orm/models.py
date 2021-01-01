# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import datetime
from orm.manage import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from status_type import StatusSendChoice, MsgTypeChoice


class ActionModel(db.Model):

    __tablename__ = "action"
    __table_args__ = {
        "schema": "manager",
        "comment": "Операции"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_id = db.Column("task_id", UUID(as_uuid=True), db.ForeignKey("task.s_id"), nullable=False, info={"verbose_name": "Задача"})
    method_id = db.Column("method_id", UUID(as_uuid=True), db.ForeignKey("method.s_id"), nullable=False, info={"verbose_name": "Метод службы"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    number = db.Column("number", db.Integer, default=1, info={"verbose_name": "Порядковый номер"})

    # task = db.relationship("TaskModel", backref=db.backref("action_list", lazy="dynamic"))
    # method = db.relationship("MethodModuleModel", backref=db.backref("action_list", lazy="dynamic"))

    def __init__(self, task, method, name, number=1):
        self.task = task
        self.method = method
        self.name = name
        self.number = number

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

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<BaseTaskModel {self.s_id}>"


class CommandModel(db.Model):

    __tablename__ = "command"
    __table_args__ = {
        "schema": "manager",
        "comment": "Команды"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    action_id = db.Column("action_id", UUID(as_uuid=True), db.ForeignKey("action.s_id"), nullable=False, info={"verbose_name": "Действие"})
    method_id = db.Column("method_id", UUID(as_uuid=True), db.ForeignKey("method.s_id"), nullable=False, info={"verbose_name": "Метод службы"})
    parent_id = db.Column("parent_id", UUID(as_uuid=True), db.ForeignKey("parent.s_id"), nullable=True, info={"verbose_name": "Родительская команда"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    is_parallel = db.Column("is_parallel", db.Boolean, default=False, info={"verbose_name": "Признак параллельности"})
    number = db.Column("number", db.Integer, default=1, info={"verbose_name": "Порядковый номер"})

    # action = db.relationship("ActionModel", backref=db.backref("command_list", lazy="dynamic"))
    # method = db.relationship("MethodModuleModel", backref=db.backref("command_list", lazy="dynamic"))
    # parent = db.relationship("CommandModel", backref=db.backref("command_list", lazy="dynamic"))

    def __init__(self, action, method, name, parent=None, is_parallel=False, number=1):
        self.action = action
        self.method = method
        self.name = name
        self.parent = parent
        self.is_parallel = is_parallel
        self.number = number

    def __repr__(self):
        return f"<CommandModel {self.s_id}>"


class CommandLogModel(db.Model):

    __tablename__ = "command_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения команд"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("task_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения задач"})
    parent_id = db.Column("parent_id", UUID(as_uuid=True), db.ForeignKey("parent.s_id"), nullable=True, info={"verbose_name": "Родительская выполняемая команда"})
    command_id = db.Column("command_id", UUID(as_uuid=True), db.ForeignKey("command.s_id"), nullable=False, info={"verbose_name": "Команда"})
    status_id = db.Column("status_id", UUID(as_uuid=True), db.ForeignKey("status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})

    # task_log = db.relationship("TaskLogModel", backref=db.backref("command_log_list", lazy="dynamic"))
    # parent = db.relationship("CommandLogModel", backref=db.backref("command_log_list", lazy="dynamic"))
    # command = db.relationship("CommandModel", backref=db.backref("command_log_list", lazy="dynamic"))
    # status = db.relationship("TaskStatusModel", backref=db.backref("command_log_list", lazy="dynamic"))

    def __init__(self, task_log, command, status, parent=None):
        self.task_log = task_log
        self.command = command
        self.status = status
        self.parent = parent

    def __repr__(self):
        return f"<CommandLogModel {self.s_id}>"


class MainTaskLogModel(db.Model):

    __tablename__ = "main_task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения базовых задач"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    base_task_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("base_task.s_id"), nullable=False, info={"verbose_name": "Базовая задача"})
    status_id = db.Column("status_id", UUID(as_uuid=True), db.ForeignKey("status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})
    add_task_date = db.Column("add_task_date", db.DateTime, default=datetime.now, info={"verbose_name": "Дата и время постановки задачи"})
    exec_task_date = db.Column("exec_task_date", db.DateTime, nullable=True, info={"verbose_name": "Дата и время начала выполнения задачи"})
    end_task_date = db.Column("end_task_date", db.DateTime, nullable=True, info={"verbose_name": "Дата и время окончания выполнения задачи"})

    # base_task = db.relationship("BaseTaskModel", backref=db.backref("main_task_log_list", lazy="dynamic"))
    # status = db.relationship("TaskStatusModel", backref=db.backref("main_task_log_list", lazy="dynamic"))

    def __init__(self, base_task, status, exec_task_date=None, end_task_date=None):
        self.base_task = base_task
        self.status = status
        self.exec_task_date = exec_task_date
        self.end_task_date = end_task_date

    def __repr__(self):
        return f"<MainTaskLogModel {self.s_id}>"


class MessageModel(db.Model):

    __tablename__ = "message"
    __table_args__ = {
        "schema": "manager",
        "comment": "Сообщения"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("base_task.s_id"), nullable=True, info={"verbose_name": "Аудит выполнения задач"})
    command_log_id = db.Column("command_log_id", UUID(as_uuid=True), db.ForeignKey("command_log.s_id"), nullable=True, info={"verbose_name": "Аудит выполнения команд"})
    parent_msg_id = db.Column("parent_msg_id", UUID(as_uuid=True), db.ForeignKey("parent_msg.s_id"), nullable=True, info={"verbose_name": "Родительское сообщение"})
    send_id = db.Column("send_id", UUID(as_uuid=True), db.ForeignKey("send.s_id"), nullable=True, info={"verbose_name": "Отправитель"})
    get_id = db.Column("get_id", UUID(as_uuid=True), db.ForeignKey("get.s_id"), nullable=False, info={"verbose_name": "Получатель"})
    data = db.Column("data", JSONB, nullable=True, info={"verbose_name": "Данные"})
    msg_type = db.Column("name", db.Enum(MsgTypeChoice), default=MsgTypeChoice.connect.value, info={"verbose_name": "Тип сообщения"})
    status = db.Column("status", db.Enum(StatusSendChoice), default=StatusSendChoice.sent.value, info={"verbose_name": "Статус отправки"})
    date_created = db.Column("date_created", db.DateTime, default=datetime.now, info={"verbose_name": "Дата создания"})

    # task_log = db.relationship("TaskLogModel", backref=db.backref("message_list", lazy="dynamic"))
    # command_log = db.relationship("CommandLogModel", backref=db.backref("message_list", lazy="dynamic"))
    # parent_msg = db.relationship("MessageModel", backref=db.backref("message_list", lazy="dynamic"))
    # send = db.relationship("ModuleModel", backref=db.backref("send_message_list", lazy="dynamic"))
    # get = db.relationship("ModuleModel", backref=db.backref("get_message_list", lazy="dynamic"))

    def __init__(self, task_log, get, msg_type, status, command_log=None, parent_msg=None, send=None):
        self.task_log = task_log
        self.get = get
        self.command_log = command_log
        self.parent_msg = parent_msg
        self.send = send
        self.msg_type = msg_type
        self.status = status

    def __repr__(self):
        return f"<MessageModel {self.s_id}>"


class MethodModuleModel(db.Model):

    __tablename__ = "method_module"
    __table_args__ = {
        "schema": "manager",
        "comment": "Методы функциональных служб"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    module_id = db.Column("module_id", UUID(as_uuid=True), db.ForeignKey("module.s_id"), nullable=False, info={"verbose_name": "Служба"})
    name = db.Column("name", db.Text, nullable=False, info={"verbose_name": "Наименование"})
    system_name = db.Column("system_name", db.Text, nullable=False, info={"verbose_name": "Системное наименование"})

    # module = db.relationship("ModuleModel", backref=db.backref("method_module_list", lazy="dynamic"))

    def __init__(self, module, system_name, name=None):
        self.module = module
        self.system_name = system_name
        self.name = system_name if not name else name

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

    def __init__(self, channel_name, system_name, name=None, status=False):
        self.channel_name = channel_name
        self.system_name = system_name
        self.name = system_name if not name else name
        self.status = status

    def __repr__(self):
        return f"<ModuleModel {self.s_id}>"


class ObjectToCommandLogModel(db.Model):

    __tablename__ = "object_to_command_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Связь Аудита выполнения команд с записью объекта"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    command_log_id = db.Column("command_log_id", UUID(as_uuid=True), db.ForeignKey("command_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения команд"})
    object_id = db.Column("object_id", UUID(as_uuid=True), nullable=False, info={"verbose_name": "Объект"})

    # command_log = db.relationship("CommandLogModel", backref=db.backref("object_to_command_log_list", lazy="dynamic"))

    def __init__(self, command_log, object_id):
        self.command_log = command_log
        self.object_id = object_id

    def __repr__(self):
        return f"<ObjectToCommandLogModel {self.s_id}>"


class ObjectToTaskLogModel(db.Model):

    __tablename__ = "object_to_task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Связь Аудита выполнения задачи с записью объекта"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    task_log_id = db.Column("task_log_id", UUID(as_uuid=True), db.ForeignKey("task_log.s_id"), nullable=False, info={"verbose_name": "Аудит выполнения задач"})
    object_id = db.Column("object_id", UUID(as_uuid=True), nullable=False, info={"verbose_name": "Объект"})

    # task_log = db.relationship("TaskLogModel", backref=db.backref("object_to_task_log_list", lazy="dynamic"))

    def __init__(self, task_log, object_id):
        self.task_log = task_log
        self.object_id = object_id

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

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<TaskModel {self.s_id}>"


class TaskLogModel(db.Model):

    __tablename__ = "task_log"
    __table_args__ = {
        "schema": "manager",
        "comment": "Аудит выполнения задач"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    main_task_log_id = db.Column("main_task_log_id", UUID(as_uuid=True), db.ForeignKey("main_task_log.s_id"), nullable=False, info={"verbose_name": ""})
    action_id = db.Column("action_id", UUID(as_uuid=True), db.ForeignKey("action.s_id"), nullable=False, info={"verbose_name": "Операция"})
    status_id = db.Column("status_id", UUID(as_uuid=True), db.ForeignKey("status.s_id"), nullable=True, info={"verbose_name": "Статус выполнения"})

    # main_task_log = db.relationship("TaskModel", backref=db.backref("task_log_list", lazy="dynamic"))
    # action = db.relationship("ActionModel", backref=db.backref("task_log_list", lazy="dynamic"))
    # status = db.relationship("StatusTaskModel", backref=db.backref("task_log_list", lazy="dynamic"))

    def __init__(self, main_task_log, action, status):
        self.main_task_log = main_task_log
        self.action = action
        self.status = status

    def __repr__(self):
        return f"<TaskLogModel {self.s_id}>"


class TaskSequenceModel(db.Model):

    __tablename__ = "task_sequence"
    __table_args__ = {
        "schema": "manager",
        "comment": "Последовательность задач"
    }

    s_id = db.Column("s_id", UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, info={"verbose_name": "Идентификатор"})
    base_task_id = db.Column("base_task_id", UUID(as_uuid=True), db.ForeignKey("base_task.s_id"), nullable=False, info={"verbose_name": "Базовая задача"})
    task_id = db.Column("task_id", UUID(as_uuid=True), db.ForeignKey("task.s_id"), nullable=False, info={"verbose_name": "Задача"})
    number = db.Column("number", db.Integer, default=1, info={"verbose_name": "Порядковый номер"})

    # base_task = db.relationship("BaseTaskModel", backref=db.backref("task_sequence_list", lazy="dynamic"))
    # task = db.relationship("TaskModel", backref=db.backref("task_sequence_list", lazy="dynamic"))

    def __init__(self, base_task, task, number=1):
        self.base_task = base_task
        self.task = task
        self.number = number

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

    def __init__(self, name, system_name):
        self.name = name
        self.system_name = system_name

    def __repr__(self):
        return f"<TaskStatusModel {self.s_id}>"

