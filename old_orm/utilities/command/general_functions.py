# -*- coding: utf-8 -*-
from itertools import zip_longest
from uuid import UUID
from subprocess import Popen, PIPE


def grouper(iterable, n):
    """
    функция для дробления итерируемого объекта на чанки размера n
    нужна, что бы сделать код более питонячным =)
    :param iterable: итерируемая последовательность
    :param n: размер чанка
    :return:
    """
    sentinel = object()
    args = [iter(iterable)] * n
    return [[entry for entry in iterable if entry is not sentinel]
            for iterable in zip_longest(*args, fillvalue=sentinel)]


def is_uuid(variable):
    """
    Является ли variable валидным UUID?
    :param variable:
    :return: True if UUID, else False
    """
    try:
        UUID(variable)
    except (AttributeError, ValueError, TypeError):
        if isinstance(variable, UUID):
            return True
        return False
    else:
        return True


def mod_update(list_or_string, value):
    """
    :param list_or_string: string or list of strings
    :param value: string
    :return: dict with key or keys, and values
    """
    result = {}

    if isinstance(list_or_string, list):
        for item in list_or_string:
            result.update({item: value})
    else:
        result.update({list_or_string: value})
    return result


def map_dtm(map_dict, data_dict):
    """
    функция осуществляет поиск в словаре data_dict значений ключей словаря map_dict:
        Если ключ найден - производится запись map_dict[value]: data_dict[key]
        Если ключ не найден то производится запись map_dict[value]: None
    :param map_dict: словарь содержащий соотношение: Ключ словаря data_dict: Ключ словаяря mapped_dict
    :param data_dict: словарь содержащий значения, которые необходимо прикрутить к новым
    :return: mapped_dict
    """
    result_dict = {}
    for key, value in map_dict.items():
        if key in data_dict.keys():
            result_dict.update(mod_update(value, data_dict[key]))
        else:
            result_dict.update(mod_update(value, None))
    return result_dict


def execute(cmnd):
    """
    :param cmnd: команды для исполнения
    :return: кортеж: (результат выполнения команд, ошибка)
    """
    try:
        p = Popen(cmnd, shell=True, stdout=PIPE, stderr=PIPE)
        res = p.communicate()
        rc = p.returncode
        res = (res[0].decode('utf-8'), res[1]) if isinstance(res[0], bytes) else (
            res[0], res[1])  # если вернётся байт строка
    except OSError as err:
        res, rc = ('error', err), 1
    res, err = res
    return res, err, rc