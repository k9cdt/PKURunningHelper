#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: util/func.py
#
# 通用函数库
#

import os
import hashlib
from .module import json


__all__ = [
    "json_dump",
    "json_load",
    "pretty_json",
    "MD5",
]


def json_dump(folder, file, data, **kw):
    """ json.dumps 函数封装

        Args:
            folder    str    json 文件所在文件夹
            file      str    json 文件名
            data             json 数据
    """
    jsonPath = os.path.join(folder, file)
    with open(jsonPath,"w",encoding="utf-8") as fp:
        fp.write(json.dumps(data, ensure_ascii=False, **kw))


def json_load(folder, file, **kw):
    """ json.loads 函数封装

        Args:
            folder    str    json 文件所在文件夹
            file      str    json 文件名
        Returns:
            data             json 数据
    """
    jsonPath = os.path.join(folder, file)
    with open(jsonPath,"r",encoding="utf-8") as fp:
        data = json.loads(fp.read(), **kw)
    return data


def pretty_json(data):
    """ 格式化输出 json 字符串，用于显示 json 包数据

        Args:
            data               json 数据
        Returns:
            jsonStr     str    json 格式化字符串
    """
    return json.dumps(data, indent=4, ensure_ascii=False)


def to_bytes(data):
    """ str -> bytes

        Args:
            data        str/bytes/int/float    原始数据
        Returns:
            bytes       bytes                  二进制数据
        Raises:
            TypeError   输入了非法数据类型
    """
    if isinstance(data, bytes):
        return data
    elif isinstance(data, (str, int, float)):
        return str(data).encode("utf-8")
    else:
        raise TypeError


""" hashlib 函数库封装

    Args:
        data         str/bytes/int/float    输入数据
    Returns:
        hexHash      十六进制 hash 摘要
    Raises:
        TypeError    输入了非法数据类型
"""
MD5 = lambda data: hashlib.md5(to_bytes(data)).hexdigest()

