# -*- coding: utf-8 -*-
import json
import signal
import time

from datetime import datetime
from pgnotify import await_pg_notifications, get_dbapi_connection
from psycopg2 import extras
from psycopg2.errors import lookup
from wrapper import message_wrapper, task_wrapper

from thread_pool import ThreadPool
from exceptions import FindModuleError, TaskError
from status_type import MsgTypeChoice


class BaseSVC(object):
    """
    Базовый класс службы

    Основные функции:
     - подписка на канал
     - выполнение задач в однопоточном или многопоточном режиме с одной очередью
     - выполнение периодической и/или первичной задачи по условию

    """
    _connect_string = "host={0} port={1} dbname={2} user={3}"
    _signals_to_handle = [signal.SIGINT, signal.SIGTERM]
    _host = None
    _port = None
    _db_name = None
    _user = None
    _channel_name = None
    _thread_count = None
    _table_list = None
    _e = None
    _is_period = True

    pool_task = None
    ldt = None

    def __init__(self, thread_count: int, host: str, port: str, db_name: str, user: str, channel_name: str) -> None:
        """
        Конструктор класса

        Инициализирует:
         - количество потоков
         - подключение к базе данных
         - один пул потоков

        :param thread_count: количество потоков в пуле потоков
        :param host: hostname, на которой развернута база данных
        :param port: порт подключения к базе данных
        :param db_name: наименование базы данных
        :param user: роль для подключения к базе данных
        :param channel_name: наименование канала, в который поступают сообщения от базы данных
        """
        self._host = host
        self._port = port
        self._db_name = db_name
        self._user = user
        self._thread_count = thread_count
        self._channel_name = channel_name
        self._e = get_dbapi_connection(self._connect_string.format(self._host, self._port, self._db_name, self._user))
        # TODO Создавать несколько пулов потоков, для обработки задач, которые выполняются с разной скоростью
        # TODO Либо посмотреть как настроить приоритет задач в пуле
        self.pool_task = ThreadPool(self._thread_count)

    @property
    def e(self):
        return self._e

    @property
    def is_period(self):
        return self.check_is_period()

    @property
    def table_list(self):
        return self._table_list

    @table_list.setter
    def table_list(self, table_list: list) -> None:
        self._table_list = table_list

    def _listen(self) -> None:
        """
        Подписка на список каналов

        Основыне задачи метода:
         - подписка на канал
         - ожидание сообщений
            - если ни одного сообщения пока не пришло, то производится проверка
              на признак запуска периодической/первичной задачи
            - если пришло сообщение от одного из каналов, то запускается функция обработки данного сообщения

        :return:
        """
        if self._table_list:
            is_continue = True
            while is_continue:
                try:
                    for n in await_pg_notifications(
                            self._e,
                            [self._channel_name],
                            timeout=10,
                            yield_on_timeout=True,
                            handle_signals=self._signals_to_handle,
                    ):
                        if isinstance(n, int):
                            sig = signal.Signals(n)
                            is_continue = False
                            break
                        elif n is None:
                            if self.is_period:
                                self.period_task()
                        elif n is not None:
                            if n.payload in self._table_list:
                                self.add_task(n.channel, n.payload)
                except lookup("08000"):
                    time.sleep(10)
                except KeyboardInterrupt:
                    if self.pool_task:
                        del self.pool_task

    def _get_data(self, query: str) -> list:
        """
        Получение результата запроса

        :param query: запрос
        :return: список полученных записей
        """
        cursor = self.e.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query)
        data = cursor.fetchall()
        key_list = [row[0] for row in cursor.description]
        data = [{key: item if item else "" for key, item in zip(key_list, line)} for line in data]
        cursor.close()
        return data

    def _execute(self, query: str) -> None:
        """
        Выполнение запроса с коммитом

        :param query: запрос
        :return:
        """
        cursor = self.e.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query)
        self.e.commit()
        cursor.close()

    def run(self) -> None:
        """
        Запуск подписки на список каналов

        :return:
        """
        self._listen()

    def add_task(self, channel: str, data: str) -> None:
        """
        Обработка сообщения из канала

        :param channel: наименование канала
        :param data: данные из канала
        :return:
        """
        pass

    def period_task(self) -> None:
        """
        Периодическая/первичная задача

        :return:
        """
        self.ldt = datetime.now()

    def check_is_period(self) -> bool:
        """
        Проверка на запуск периодической/первичной задачи
        В данном случае периодическая/первичная задача будет запускаться один раз при старте

        :return: True или False
        """
        return True if not self.ldt else False


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
        self.module = system_name
        self.manager = manager_name

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, system_name: str) -> None:
        self._module = self._get_module_info(system_name)

    def _get_module_info(self, system_name: str) -> dict:
        try:
            query = f"SELECT * FROM manager.module WHERE system_name = '{system_name}'"
            data = self._get_data(query)
        except Exception as ex:
            message = f"Ошибка при выполнения запроса {query}: {ex}"
            raise FindModuleError(message)
        if not data:
            message = "Модуля с указанным системным наименованием не существует"
            raise FindModuleError(message)
        elif len(data) > 1:
            message = "Существует несколько модулей с указанным системным наименованием"
            raise FindModuleError(message)
        return data[0]

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

        P.S. Я знаю, что в python нет такого понятия - как закрытые и открытые методы,
        и на самом деле вызвать _listen можно, но прошу так не делать.

        :return:
        """
        self.table_list = [self.module["channel_name"]]
        BaseSVC.run(self)
        self.module["status"] = False

        query = "UPDATE status = {status} WHERE s_id = '{s_id}'".format(
            status=self.module["status"], s_id=self.module["s_id"])
        self._execute(query)

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
    def _connect(self, *args, **kwargs) -> (bool, dict):
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
    def _error_method(self, *args, **kwargs) -> (bool, dict):
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
        return None, True, kwargs.get("data")
