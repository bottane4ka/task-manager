# -*- coding: utf-8 -*-
import signal
import time
import json

from datetime import datetime
from pgnotify import await_pg_notifications, get_dbapi_connection
from psycopg2.errors import lookup

# sys.path.insert(1, (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))))
#
# import django_import


# from api_task import settings
from api_task.thread_pool import ThreadPool
from api_task.wrapper import task_wrapper
from api_task.wrapper import message_wrapper
from api_task.exceptions import FindModuleError, TaskError

from task.models import MsgTypeChoice
from task.models import ModuleModel
from task.models import MessageModel
from api_task.base_class import BaseSVC




class BasePeriodicSVC(object):

    _module = None
    # _task_module = None
    _period_time = None
    _is_period = True
    ldt = None

    def __init__(self, system_name: str, period_time: int) -> None:
        self.module = system_name
        self.period_time = period_time
        # self.task_module = MODULE_SYSTEM_NAME

    @property
    def module(self):
        """
        Получение записи о функциональной службе
        :return: запись о функциональной службе
        """
        return self._module

    @module.setter
    def module(self, system_name: str) -> None:
        """
        Инициализация записи функциональной службы
        :param system_name: системное наименование функциональной службы
        :return:
        """
        try:
            self._module = ModuleModel.objects.get(system_name=system_name)
        except ModuleModel.DoesNotExist:
            message = "Службы с указанным системным наименованием не существует в базе данных"
            raise FindModuleError(message)
        except ModuleModel.MultipleObjectsReturned:
            message = "Существует несколько служб с указанным системным наименованием в базе данных"
            raise FindModuleError(message)

    @property
    def period_time(self):
        """
        Время в секундах, которое проходит между выполнением периодическими задачами
        :return:
        """
        return self._period_time

    @period_time.setter
    def period_time(self, period_time: int) -> None:
        self._period_time = period_time

    @property
    def is_period(self):
        return self.check_is_period()

    def _period_task(self):
        while True:
            try:
                if self.is_period:
                    self.period_task()
            except Exception as ex:
                break

    def run(self):
        """
        :return:
        """
        self.module.status = True
        self.module.save()
        self._period_task()
        self.module.status = False
        self.module.save()

    def check_is_period(self):
        if not self.ldt:
            self.ldt = datetime.now()
            return True
        if (datetime.now() - self.ldt).seconds > self.period_time:
            return True
        return False

    def period_task(self):
        self.ldt = datetime.now()
