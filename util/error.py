#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: util/error.py
#
# 错误类定义
#

from .module import JSONDecodeError


__all__ = [
    "JSONDecodeError",

    "PBError",
    "PBStateCodeError",

    "PKURunnerError",
    "PKURunnerSuccessStateError",
    "PKURunnerUnauthorizedError",

    "IAAAError",
    "IAAASuccessStateError",
]


class PBError(Exception):
    """ PB 错误类 """
    pass

class PBStateCodeError(PBError):
    """ PB 异常请求码 """
    pass


class PKURunnerError(Exception):
    """ PKURunner 错误类 """
    pass

class PKURunnerSuccessStateError(PKURunnerError):
    """ PKURunner 返回数据包 success 字段为 false ，异常请求结果 """
    pass

class PKURunnerUnauthorizedError(PKURunnerError):
    """ PKURunner 鉴权错误 """
    pass


class IAAAError(PKURunnerError):
    """ IAAA 错误类 """
    pass

class IAAASuccessStateError(IAAAError):
    """ IAAA 返回数据包 success 字段为 false ，异常请求结果 """
    pass
