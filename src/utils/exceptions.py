# -*- coding: utf-8 -*-


class FindModuleError(Exception):
    """
    Ошибка поиска модуля в БД
    """
    pass


class TaskError(Exception):
    """
    Ошибка если идентификатор из сущности "Сообщения" не указан или указан неверный
    """
    pass


class WorkError(Exception):
    pass
