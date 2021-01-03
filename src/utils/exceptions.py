# -*- coding: utf-8 -*-


class FindModuleError(Exception):
    """
    Ошибка поиска службы в базе данных
    """
    pass


class TaskError(Exception):
    """
    Ошибка если идентификатор из сущности "Сообщения" не указан или указан неверный
    """
    pass


class WorkError(Exception):
    """
    Ошибка выполнения задачи
    """
    pass
