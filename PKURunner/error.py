#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: PKURunner/error.py
#
# 错误类
#

__all__ = [
    "PKURunnerError",
    "PKURunnerRequestStatusError",
    "PKURunnerSuccessStateError",
    "PKURunnerUnauthorizedError",
    "PKURunnerNotVerifiedError",

    "IAAAError",
    "IAAARequestStatusError",
    "IAAASuccessStateError",
]


class PKURunnerError(Exception):
    """ PKURunner 错误类 """
    pass

class PKURunnerRequestStatusError(PKURunnerError):
    """ PKURunner 请求状态码异常 """
    pass

class PKURunnerSuccessStateError(PKURunnerError):
    """ PKURunner 返回数据包 success 字段为 false ，异常请求结果 """
    pass

class PKURunnerUnauthorizedError(PKURunnerError):
    """ PKURunner 鉴权错误 """
    pass

class PKURunnerNotVerifiedError(PKURunnerError):
    """ PKURUnner 上传记录无效 """
    pass


class IAAAError(PKURunnerError):
    """ IAAA 错误类 """
    pass

class IAAARequestStatusError(IAAAError):
    """ IAAA 请求状态码异常 """

class IAAASuccessStateError(IAAAError):
    """ IAAA 返回数据包 success 字段为 false ，异常请求结果 """
    pass
