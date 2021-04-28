# -*- coding: utf-8 -*-
from enum import Enum


class StatusSendChoice(Enum):
    sent = 'Отправлено'
    recd = 'Получено'
    ok = 'Обработано'


class MsgTypeChoice(Enum):
    connect = 'Подключение'
    task = 'Задача'
    info = 'Информация'
    success = 'Выполнено'
    error = 'Ошибка'
    warning = 'Внимание'


