from datetime import datetime
from functools import wraps

from rest.manager.models import MessageModel
from rest.manager.models import ObjectToCommandLogModel
from rest.manager.models import ObjectToTaskLogModel
from rest.manager.models import StatusSendChoice, MsgTypeChoice
from rest.manager.models import TaskLogModel


def task_wrapper(func):
    """
    Декоратор обработки сообщения из сущности "Сообщения"

    Основные задачи декоратора:
     - "квитироване" пришедшего сообщения, если оно указано:
        - перед выполнением функции - изменение статуса отправки на "Получено"
        - после выполнения функции (не зависимо от признака ошибки) - изменение статуса отправки на "Отработано")
    - запуск декорируемой функции с пришедшими параметрами (функция должна сама обрабатывать raise,
      либо должна быть обернута в декоратор @logger)
    - создание записи в сущности "Сообщения" с результатом выполнения функции, с ссылкой на пришедшее сообщение и задачу
      (если указано)

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
                     - task - идентификатор сообщения из сущности "Сообщения"
                     - msg_type - тип сообщения
                     - sender - отправитель (данная служба)
                     - recipient - получатель (менеджер задач)
        :return:
        """
        task = kwargs.pop("task", None)
        msg_type = kwargs.pop("msg_type")
        sender = kwargs.pop("sender", None)
        recipient = kwargs.pop("recipient", None)
        is_error = False
        if task:
            try:
                task = MessageModel.objects.get(id=task)
            except MessageModel.DoesNotExist:
                is_error = True

        if not is_error:
            if task:
                task.status = StatusSendChoice.recd.value
                task.save()

            result, is_error, data = func(*args, task=task, **kwargs)

            post_data = {
                "sender": sender if not task else task.sender,
                "recipient": recipient if not task else task.recipient,
                "date_created": datetime.now(),
                "status": StatusSendChoice.sent.value,
            }

            if msg_type == MsgTypeChoice.connect.value:
                post_data["msg_type"] = MsgTypeChoice.connect.value
            elif data and "msg_type" in data:
                post_data["msg_type"] = data["msg_type"]
            else:
                post_data["msg_type"] = (
                    MsgTypeChoice.error.value
                    if is_error
                    else MsgTypeChoice.success.value
                )

            if task:
                post_data["parent_msg"] = task.id
                post_data["task_log"] = task.task_log
                post_data["command_log"] = task.command_log

            if data:
                post_data["data"] = data

            MessageModel.objects.create(**post_data)

            if task:
                task.status = StatusSendChoice.ok.value
                task.save()

    return wrapper


def task_model_wrapper(model):
    """
    Декоратор для указания модели Django

    :param model: модель Django
    :return:
    """

    def model_wrapper(func):
        """
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
                         - task - идентификатор сообщения из сущности "Сообщения"
                         - msg_type - тип сообщения
                         - sender - отправитель (данная служба)
                         - recipient - получатель (менеджер задач)

            :return: при успешном поиске объекта возвращается ответ декорируемой функции
                     иначе:
                           - result = None
                           - is_error = True - признак ошибки
                           - data - данные для сохранения в сущности "Сообщения"
                             (с ключом message для отображения в пользовательском интерфейсе)
            """
            task = kwargs.pop("task", None)
            object_list = None
            if task:
                object_to_task_log_list = None
                task_log_list = TaskLogModel.objects.filter(
                    action__number__lte=task.task_log.action.number,
                    main_task_log=task.task_log.main_task_log,
                ).order_by("-action__number")
                for task_log in task_log_list:
                    object_to_task_log_list = ObjectToTaskLogModel.objects.filter(
                        task_log=task_log
                    )
                    if object_to_task_log_list:
                        break

                if not object_to_task_log_list:
                    message = (
                        f"Не существует связанных объектов с задачей {task.task_log}"
                    )
                    return None, True, {"message": message}
                object_id_list = set(
                    [
                        object_to_task_log.object
                        for object_to_task_log in object_to_task_log_list
                    ]
                )
                if not model._meta.pk:
                    message = f"Не существует первичного ключа в сущности {model.db_table}"
                    return None, True, {"message": message}
                object_list = model.objects.filter(
                    **{f"{model._meta.pk.name}__in": object_id_list}
                )
                if not object_list:
                    message = f"В сущности {model.db_table} не существует записи с идентификаторами {', '.join(object_id_list)}"
                    return None, True, {"message": message}

            return func(*args, task=task, object_list=object_list, **kwargs)

        return wrapper

    return model_wrapper


def command_model_wrapper(model):
    """
    Декоратор для указания модели Django

    :param model: модель Django
    :return:
    """

    def model_wrapper(func):
        """
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
                         - task - идентификатор сообщения из сущности "Сообщения"
                         - msg_type - тип сообщения
                         - sender - отправитель (данная служба)
                         - recipient - получатель (менеджер задач)

            :return: при успешном поиске объекта возвращается ответ декорируемой функции
                     иначе:
                           - result = None
                           - is_error = True - признак ошибки
                           - data - данные для сохранения в сущности "Сообщения"
                             (с ключом message для отображения в пользовательском интерфейсе)
            """
            task = kwargs.pop("task", None)
            object_id = None
            if task:
                try:
                    related_object = ObjectToCommandLogModel.objects.get(
                        command_log=task.command_log
                    ).related_object
                except ObjectToCommandLogModel.DoesNotExist:
                    message = f"Не существует необходимого связанного объекта с командой {task.command_log.id}"
                    return None, True, {"message": message}
                except ObjectToCommandLogModel.MultipleObjectsReturned:
                    message = f"Существует больше одного связанного объекта с командой {task.command_log.id}"
                    return None, True, {"message": message}
                else:
                    if not model._meta.pk:
                        message = f"Не существует первичного ключа в сущности {model.db_table}"
                        return None, True, {"message": message}
                    try:
                        object_id = model.objects.get(
                            **{f"{model._meta.pk.name}": related_object}
                        )
                    except model.DoesNotExist:
                        message = f"В сущности {model.db_table} не существует записи с идентификатором {related_object.id}"
                        return None, True, {"message": message}

            return func(*args, task=task, object_id=object_id, **kwargs)

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
                      - task - идентификатор сообщения из сущности "Сообщения"
        :return: возврат ответа декорируемой функции
        """
        task = kwargs.pop("task")
        result, is_error, data = func(*args, task=task, **kwargs)
        if data:
            msg_type = data.pop("msg_type", None)
            if not msg_type:
                msg_type = MsgTypeChoice.info.value
            post_data = {
                "sender": task.sender,
                "recipient": task.recipient,
                "date_created": datetime.now(),
                "status": StatusSendChoice.sent.value,
                "msg_type": msg_type,
                "parent_msg": task,
                "task_log": task.task_log,
                "command_log": task.command_log,
                "data": data,
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
