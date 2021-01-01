# -*- coding: utf-8 -*-

import syslog
import sys
import traceback
from functools import wraps
from django.conf import settings


def logger(module_tag):
    """
    декоратор для упрощения логирования, просто оберните функцию
    вызываемую в представлении данным декоратором и передайте
    ей наименование модуля
    ВАЖНО!: декорируемая функция должна возвращать кортеж:
    return result, is_error, data, ;где
    result - стандартный результат выполнения функции, то что
             функция бы вернула без декоратора
    data - сообщение с обязательным ключом message
    is_error - True или False указывающее на то, произошла ли ошибка
            процессе выполнения запроса если этот
            параметр True - будет вызвано APIException DRF
    :param module_tag: наименование модуля
    :return: результат ее выполнения
    """
    def logger_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            syslog.openlog(settings.SYS_LOG_NAME)
            try:
                result, is_error, data = func(*args, **kwargs)
            except Exception as err:
                syslog.syslog(syslog.LOG_ERR,
                              '{}: Произошел незапланированный сбой!!! Traceback:'.format(module_tag))
                ex_type, ex, tb = sys.exc_info()
                for obj in traceback.extract_tb(tb):
                    syslog.syslog(syslog.LOG_ERR,
                                  'Файл: {}, строка: {}, вызов: {}'.format(obj[0],
                                                                           obj[1],
                                                                           obj[2]))
                    syslog.syslog(syslog.LOG_ERR, '----->>>  {}'.format(obj[3]))
                syslog.syslog(syslog.LOG_ERR, '{}: Текст ошибки: {}.'.format(module_tag, err))
                return None, True, {"message": str(err)}
            else:
                if is_error and data and "message" in data:
                    syslog.syslog(syslog.LOG_ERR, '{}: {}'.format(module_tag, data["message"]))
                if data and "message" in data:
                    syslog.syslog(syslog.LOG_INFO, '{}: {}'.format(module_tag, data["message"]))
            return result, is_error, data
        return wrapper
    return logger_decorator
