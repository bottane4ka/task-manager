#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple

ICTuple = namedtuple("ICTuple", ("path", "summ"))

ResultTuple = namedtuple("Result", ("result", "message"))

LogMessage = namedtuple("Message", "ok error")

