#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: Joyrun/error.py
#
# 错误类
#

__all__ = [
    "JoyrunError",
    "JoyrunRequestStatusError",
    "JoyrunRetStateError",
    "JoyrunSidInvalidError",
]


class JoyrunError(Exception):
    """ Joyrun 错误类 """
    pass

class JoyrunRequestStatusError(JoyrunError):
    """ Joyrun 请求状态码异常 """
    pass

class JoyrunRetStateError(JoyrunError):
    """ Joyrun 返回数据包 ret 字段非 0 ，请求结果异常 """
    pass

class JoyrunSidInvalidError(JoyrunRetStateError):
    """ Joyrun 请求结果 ret 401 ，sid 失效，账号异地登录或 sid 过期 """
    pass