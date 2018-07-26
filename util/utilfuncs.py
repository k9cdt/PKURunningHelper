#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: util/utilfuncs.py


import os

try:
    import simplejson as json
except ModuleNotFoundError:
    import json


__all__ = [
    "json_dump",
    "json_load",
]


def json_dump(folder, file, data, **kw):
    jsonPath = os.path.join(folder, file)
    with open(jsonPath,"w") as fp:
        fp.write(json.dumps(data, ensure_ascii=False, **kw))

def json_load(folder, file, **kw):
    jsonPath = os.path.join(folder, file)
    with open(jsonPath,"r") as fp:
        data = json.loads(fp.read(), **kw)
    return data
