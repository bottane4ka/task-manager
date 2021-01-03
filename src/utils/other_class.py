# -*- coding: utf-8 -*-
import json
from datetime import datetime

from utils.exceptions import FindModuleError, TaskError
from utils.wrapper import message_wrapper, task_wrapper
from utils.base_utils.base_class import BaseSVC
from utils.status_type import MsgTypeChoice

from sqlalchemy.orm import Session
from sqlalchemy.orm import exc
from orm.models import ModuleModel


class BaseFunctionalSVC(BaseSVC):
    """
    Базовый класс функциональной службы

    Основные задачи:
     - подписка на канал, который прописан в базе данных в сущности "Службы и модули" для соответствующего модуля
     - запуск первичной задачи: уведомление менеджера задач о начале работы
     - при получении сообщения:
        - обработка сообщения (предполагается, что сообщение - это json, преобразованный в строку)
        - получение метода из сообщения (обязательный атрибут сообщения; если его нет, то отправляется ответ об ошибке)
        - поиск соответствующего метода в классе
        - запуск метода класса с пришедшими остальными данными
    """

    _module = None
    _manager = None

    def __init__(self, system_name: str, thread_count: int, host: str, port: str, db_name: str, user: str,
                 channel_name: str, manager_name: str) -> None:
        """
        Конструктор класса

        Инициализирует:
         - все параметры из базового класса
         - данные функциональной службе
         - данные о менеджере задач

        :param system_name: системное наименование функциональной службы
        :param thread_count: количество потоков для пула потоков
        :param host: hostname, на которой развернута база данных
        :param port: порт подключения к базе данных
        :param db_name: наименование базы данных
        :param user: роль для подключения к базе данных
        :param channel_name: наименование канала, в который поступают сообщения от базы данных
        :param manager_name: системное наименование менеджера задач
        """
        BaseSVC.__init__(self, thread_count, host, port, db_name, user, channel_name)
        self.session = Session(bind=self.e)
        self.module = system_name
        self.manager = manager_name

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, system_name: str) -> None:
        self._module = self._get_module_info(system_name)

    def _get_module_info(self, system_name: str) -> ModuleModel:
        try:
            data = self.session.query(ModuleModel).filter(ModuleModel.system_name == system_name).one()
        except exc.NoResultFound:
            message = f"Ошибка. Не существует службы {system_name}"
            raise FindModuleError(message)
        except exc.MultipleResultsFound:
            message = f"Ошибка. Существует несколько служб {system_name}"
            raise FindModuleError(message)
        return data

    @property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, system_name: str) -> None:
        self._manager = self._get_module_info(system_name)

    def run(self):
        """
        Запуск подписки на список каналов

        Основные задачи метода:
         - инициализация списка каналов для функциональной службы
         - запуск данного метода базового класса службы (так как _listen базового класса - закрытый)

        :return:
        """
        self.table_list = [self.module["channel_name"]]
        BaseSVC.run(self)
        self.module.status = False
        self.session.commit()

    def add_task(self, channel: str, data: str) -> None:
        """
        Обработка сообщения из канала

        Алгоритм:
         - конвертирование сообщения в словарь (json)
         - получение идентификатора сообщения (обязательный аргумент)
         - получение типа сообщения (обязательный аргумент)
            - если тип сообщения "Подключение" (connect), то запуск метода на отправку сообщения о подключении
              (без добавления в очередь, так как при запросе на сообщение о "Подключении" от менеджера задач
               необходимо ответить быстро)
            - если тип сообщения не "Подключение", значит пришло сообщение с типом "Задача", тогда
                - получение метода из сообщения (обязательный аргумент)
                - поиск соответствующего метода в классе
                - добавление в очередь на выполнение данного метода со всеми пришедшими данными
                - если метода в сообщении нет или не существует соответствующего метода класса,
                  то вызывается метод на отправку сообщения об ошибке

        :param channel: наименование канала, из которого пришло сообщение
        :param data: данные сообщения
        :return:
        """
        data = json.loads(data)
        task_id = data.pop("task_id")

        msg_type = data.get("msg_type")
        if msg_type == MsgTypeChoice.connect.value:
            # data["method"] = "connect"
            self._connect([task_id] if task_id else None, task_id=task_id, data=data, msg_type=msg_type,
                          send_id=self.module, get_id=self.manager)
        else:
            try:
                method = data.get("method", None)
                if not method:
                    message = "Неверный формат сообщения: не указан ключ method"
                    raise TaskError(message)
                try:
                    func = getattr(self, data["method"])
                except AttributeError:
                    message = "{} не имеет метод {}".format(self.module["name"], data["method"])
                    raise TaskError(message)

                self.pool_task.add_task(func, task_id=task_id, **data)
            except TaskError as ex:
                self.pool_task.add_task(self._error_method, task_id=task_id, data={"message": str(ex)},
                                        send_id=self.module, get_id=self.manager)

    def period_task(self) -> None:
        """
        Периодическая/первичная задача

        Основные задачи метода:
         - инициализация даты и времени запуска данной задачи
         - "инсценирование" сообщения из канала на подключение

        :return: -
        """
        self.ldt = datetime.now()
        data = {"msg_type": MsgTypeChoice.connect.value, "task_id": None}
        self.add_task("", json.dumps(data))

    @message_wrapper
    @task_wrapper
    def _connect(self, *args, **kwargs) -> (None, bool, None):
        """
        Метод на отправку сообщения о подключении.

        Всю работу выполняет декоратор @task_wrapper

        :param args:
        :param kwargs:
                     - task_id - идентификатор сообщения из сущности "Сообщения"
                     - msg_type - тип сообщения
                     - send_id - отправитель (данная служба)
                     - get_id - получатель (менеджер задач)
        :return: кортеж:
                     - result = None - результат выполнения метода
                     - is_error = False - признак ошибки
                     - data = None - данные для сохранения в сущности "Сообщения"
        """
        return None, False, None

    @task_wrapper
    def _error_method(self, *args, **kwargs) -> (None, bool, dict):
        """
        Метод на отправку сообщения об ошибке при поиске метода.

        Всю работу выполняет декоратор @task_wrapper

        :param args:
        :param kwargs:
                     - task_id - идентификатор сообщения из сущности "Сообщения"
                     - msg_type - тип сообщения
                     - send_id - отправитель (данная служба)
                     - get_id - получатель (менеджер задач)
        :return: кортеж:
                     - result = None - результат выполнения метода
                     - is_error = True - признак ошибки
                     - data - данные для сохранения в сущности "Сообщения"
                       (с ключом message для отображения в пользовательском интерфейсе)
        """
        return None, True, kwargs["data"]
