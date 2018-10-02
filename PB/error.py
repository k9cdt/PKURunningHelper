#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: PB/error.py
#
# 错误类
#

__all__ = [
    "PBError",
    "PBStateCodeError",
]


class PBError(Exception):
    """ PB 错误类 """
    pass

class PBStateCodeError(PBError):
    """ PB 异常请求码 """
    pass