# -*- coding: utf-8 -*-
import signal
from datetime import datetime
from pgnotify import await_pg_notifications, get_dbapi_connection
from thread_pool import ThreadPool


class BaseSVC(object):
    """
    Базовый класс службы

    Основные функции:
     - подписка на канал
     - выполнение задач в однопоточном или многопоточном режиме с одной очередью
     - выполнение периодической и/или первичной задачи по условию

    """
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

    connect_string = "host={0} port={1} dbname={2} user={3}"
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
        self._e = self.connect()
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
                except KeyboardInterrupt:
                    if self.pool_task:
                        del self.pool_task

    def run(self) -> None:
        """
        Запуск подписки на список каналов

        :return:
        """
        self._listen()

    def connect(self):
        """
        Подключение к базе данных.
        Возможно потребуется переопределение метода подключения к базе данных

        :return:
        """
        return get_dbapi_connection(self.connect_string.format(self._host, self._port, self._db_name, self._user))

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
