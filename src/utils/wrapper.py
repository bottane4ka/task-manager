# -*- coding: utf-8 -*-

import time
import copy
from sqlalchemy.orm import exc
from datetime import datetime
from functools import wraps

from status_type import StatusSendChoice
from status_type import MsgTypeChoice

from orm.models import MessageModel
from orm.models import ObjectToTaskLogModel
from orm.models import ObjectToCommandLogModel
from orm.models import TaskLogModel
from orm.models import ActionModel
from orm.models import CommandLogModel


# from django.db import transaction


# GET_MESSAGE = "SELECT * FROM manager.message WHERE s_id = '{}'"
# UPDATE_STATUS_MESSAGE = "UPDATE manager.message SET status = '{}' WHERE s_id = '{}'"
# CREATE_MESSAGE = "INSERT INTO manager.message (task_log_id, parent_msg_id, send_id, get_id, data, " \
#                  "msg_type, status, date_created, command_log_id) VALUES ({item_list})"


def task_wrapper(func):
    """
    Декоратор обработки сообщения из сущности "Сообщения"

    Основные задачи декоратора:
     - "квитироване" пришедшего сообщения, если оно указано:
        - перед выполнением функции - изменение статуса отправки на "Получено"
        - после выполнения функции (не зависимо от признака ошибки) - изменение статуса отправки на "Отработано")
    - запуск декорируемой функции с пришедшими параметрами (функция должна сама обрабатывать raise,
      либо должна быть обернута в декоратор @logger)
    - создание записи в ИР "Сообщения" с результатом выполнения функции, с ссылкой на пришедшее сообщение и задачу
      (если оно указано)

    :param func: декорируемая функция, результат которой кортеж:
                     - result - результат выполнения функции
                     - is_error - признак ошибки
                     - data - данные для сохранения в сущности "Сообщения"
                       (с ключом message для отображения в пользовательском интерфейсе)
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        :param args:
        :param kwargs:
                     - task_id - идентификатор сообщения из сущности "Сообщения"
                     - msg_type - тип сообщения
                     - send_id - отправитель (данная служба)
                     - get_id - получатель (менеджер задач)
        :return:
        """
        self = args[0]
        task_id = kwargs.pop("task_id", None)
        msg_type = kwargs.pop("msg_type")
        send_id = kwargs.pop("send_id", None)
        get_id = kwargs.pop("get_id", None)
        is_error = False
        if task_id:
            try:
                task_id = self.session.query(MessageModel).filter(MessageModel.s_id == task_id).one()
            except exc.NoResultFound:
                # message = "Не существует сообщения с идентификатором {}".format(task_id)
                is_error = True

        if not is_error:
            if task_id:
                task_id.status = StatusSendChoice.recd.value
                self.session.commit()

            result, is_error, data = func(*args, task_id=task_id, **kwargs)

            post_data = {
                "send_id": send_id if not task_id else task_id.get_id,
                "get_id": get_id if not task_id else task_id.send_id,
                "date_created": datetime.now(),
                "status": StatusSendChoice.sent.value,
            }

            if msg_type == MsgTypeChoice.connect.value:
                post_data["msg_type"] = MsgTypeChoice.connect.value
            elif data and "msg_type" in data:
                post_data["msg_type"] = data["msg_type"]
            else:
                post_data["msg_type"] = MsgTypeChoice.error.value if is_error else MsgTypeChoice.success.value

            if task_id:
                post_data["parent_msg_id"] = task_id
                post_data["task_log_id"] = task_id.task_log_id
                post_data["command_log_id"] = task_id.command_log_id

            if data:
                post_data["data"] = data

            self.session.add(MessageModel(**post_data))
            self.session.commit()

            if task_id:
                task_id.status = StatusSendChoice.ok.value
                self.session.commit()

    return wrapper


def task_model_wrapper(model):
    """
    Декоратор для указания модели SQLAlchemy

    :param model: модель SQLAlchemy
    :return:
    """

    def model_wrapper(func):
        """
        Декоратор получения соответствующей записи из указанной модели
        (предполагается, что первичную информацию вводит пользователь,
         и в момент сохранения записи о каком-либо объекте производится сопоставление
         выполняемой задач с созданным объектом)

        Основные задачи декоратора:
         - получение задачи из сущности "Аудит выполнения задач" верхнего уровня
         - получение записи из сущности "Связь аудита выполнения задач с объектами"
         - получение идентификаторов объектов
         - получение записи из модели с указанным идентификатором
         - запуск декорируемой функции с пришедшими параметрами и полученной записи объекта
           (функция должна сама обрабатывать raise, либо должна быть обернута в декоратор @logger)

        :param func: декорируемая функция, результат которой кортеж:
                     - result - результат выполнения функции
                     - is_error - признак ошибки
                     - data - данные для сохранения в сущности "Сообщения"
                       (с ключом message для отображения в пользовательском интерфейсе)
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            :param args:
            :param kwargs:
                         - task_id - идентификатор сообщения из сущности "Сообщения"
                         - msg_type - тип сообщения
                         - send_id - отправитель (данная служба)
                         - get_id - получатель (менеджер задач)

            :return: при успешном поиске объекта возвращается ответ декорируемой функции
                     иначе:
                           - result = None
                           - is_error = True - признак ошибки
                           - data - данные для сохранения в сущности "Сообщения"
                             (с ключом message для отображения в пользовательском интерфейсе)
            """
            self = args[0]
            task_id = kwargs.pop("task_id", None)
            object_list = None
            if task_id:
                object_to_task_log_list = None
                task_log_list = self.session.query(TaskLogModel).filter()
                # task_log_list = TaskLogModel.objects.filter(
                #     action_id__number__lte=task_id.task_log_id.action_id.number,
                #     main_task_log_id=task_id.task_log_id.main_task_log_id
                # ).order_by("-action_id__number")
                for task_log_id in task_log_list:
                    object_to_task_log_list = ObjectToTaskLogModel.objects.filter(task_log_id=task_log_id)
                    if object_to_task_log_list:
                        break

                if not object_to_task_log_list:
                    message = "Не существует связанных объектов с задачей {}".format(task_id.task_log_id.s_id)
                    return None, True, {"message": message}
                object_id_list = set([object_to_task_log.object_id for object_to_task_log in object_to_task_log_list])
                object_list = model.objects.filter(pk__in=object_id_list)
                if not object_list:
                    message = "В сущности {} не существует записи с идентификаторами {}".format(
                        model._meta.verbose_name, ", ".join(object_id_list))
                    return None, True, {"message": message}

            return func(*args, task_id=task_id, object_list=object_list, **kwargs)

        return wrapper

    return model_wrapper


def command_model_wrapper(model):
    """
    Декоратор для указания модели SQLAlchemy

    :param model: модель SQLAlchemy
    :return:
    """

    def model_wrapper(func):
        """
        Декоратор получения соответствующей записи из указанной модели
        (предполагается, что первичную информацию передает как задачу функциональная служба,
        а менеджер задач создает эти записи)

        Основные задачи декоратора:
         - получение команды из сущности "Аудит выполнения команд"
         - получение команды из сущности "Связь Аудита выполнения команд с объектами"
         - получение идентификатора объекта (тут кажется все однозначно)
         - получение записи из модели с указанным идентификатором
         - запуск декорируемой функции с пришедшими параметрами и полученной записи объекта
           (функция должна сама обрабатывать raise, либо должна быть обернута в декоратор @logger)

        :param func: декорируемая функция, результат которой кортеж:
                     - result - результат выполнения функции
                     - is_error - признак ошибки
                     - data - данные для сохранения в сущности "Сообщения"
                       (с ключом message для отображения в пользовательском интерфейсе)
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            :param args:
            :param kwargs:
                         - task_id - идентификатор сообщения из сущности "Сообщения"
                         - msg_type - тип сообщения
                         - send_id - отправитель (данная служба)
                         - get_id - получатель (менеджер задач)

            :return: при успешном поиске объекта возвращается ответ декорируемой функции
                     иначе:
                           - result = None
                           - is_error = True - признак ошибки
                           - data - данные для сохранения в сущности "Сообщения"
                             (с ключом message для отображения в пользовательском интерфейсе)
            """
            task_id = kwargs.pop("task_id", None)
            object_id = None
            if task_id:
                try:
                    s_id = ObjectToCommandLogModel.objects.get(command_log_id=task_id.command_log_id).object_id
                except ObjectToCommandLogModel.DoesNotExist:
                    message = "Не существует необходимого связанного объекта с задачей {}".format(
                        task_id.command_log_id.s_id)
                    return None, True, {"message": message}
                except ObjectToCommandLogModel.MultipleObjectsReturned:
                    message = "Существует больше одного связанного объекта с задачей {}".format(
                        task_id.command_log_id.s_id)
                    return None, True, {"message": message}
                else:
                    try:
                        object_id = model.objects.get(pk=s_id)
                    except model.DoesNotExist:
                        message = "В сущности {} не существует записи с идентификатором {}".format(
                            model._meta.verbose_name, s_id)
                        return None, True, {"message": message}

            return func(*args, task_id=task_id, object_id=object_id, **kwargs)

        return wrapper

    return model_wrapper


def info_logger(func):
    """
    Декоратор для создания записи в сущности "Сообщения" с типом сообщения "Информация"

    Основные задачи декоратора:
     - получение записи о сообщении (обязательный атрибут, так как сообщения с типом "Информация"
       посылаются как журналирование выполнения задач)
     - запуск декорируемой функции с пришедшими параметрами (функция должна сама обрабатывать raise,
       либо должна быть обернута в декоратор @logger)
     - если признак ошибки отрицательный и поле data не пустое, то в поле data производится поиск поля тип сообщения,
        - если поля не существует, то создается запись в сущности "Сообщения" с типом "Информация"
        - иначе создается запись в сущности "Сообщения" с указанным типом (например "Внимание")

    :param func: декорируемая функция, результат которой кортеж:
                - result - результат выполнения функции
                - is_error - признак ошибки
                - data - данные для сохранения в сущности "Сообщения"
                  (с ключом message для отображения в пользовательском интерфейсе)
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        :param args:
        :param kwargs:
                      - task_id - идентификатор сообщения из сущности "Сообщения"
        :return: возврат ответа декорируемой функции
        """
        task_id = kwargs.pop("task_id")

        result, is_error, data = func(*args, task_id=task_id, **kwargs)
        if data:
            msg_type = data.pop("msg_type", None)
            if not msg_type:
                msg_type = MsgTypeChoice.info.value
            post_data = {
                "send_id": task_id.get_id,
                "get_id": task_id.send_id,
                "date_created": datetime.now(),
                "status": StatusSendChoice.sent.value,
                "msg_type": msg_type,
                "parent_msg_id": task_id,
                "task_log_id": task_id.task_log_id,
                "command_log_id": task_id.command_log_id,
                "data": data
            }

            MessageModel.objects.create(**post_data)

        return result, is_error, data

    return wrapper


def message_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        message_list = args[1]
        if message_list:
            for message in message_list:
                message.status = StatusSendChoice.recd.value
                message.save()
        func(*args, **kwargs)
        if message_list:
            for message in message_list:
                message.status = StatusSendChoice.ok.value
                message.save()

    return wrapper
