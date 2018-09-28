#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: util/module.py
#
# 统一库导入
# 用于兼容可选安装库
#

try:
    import simplejson as json
    from simplejson.errors import JSONDecodeError
except ModuleNotFoundError:
    import json
    from json.decoder import JSONDecodeError


__all__ = [
    "json",
    "JSONDecodeError",
]