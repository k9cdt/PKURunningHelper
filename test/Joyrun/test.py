#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: test.py


from itertools import permutations, combinations
from urllib.parse import quote

import sys
sys.path.append("../../")
from util import MD5

def __get_signature(params, uid, sid, salt):
    if not uid: # uid == 0 or ''
        uid = sid = ''

    return MD5("{paramsString}{salt}{uid}{sid}".format(
            paramsString = "".join("".join((k, str(v))) for k, v in sorted(params.items())),
            salt = salt,
            uid = str(uid),
            sid = sid,
        )).upper()

def get_signature_v1(params, uid=0, sid=''):
    return __get_signature(params, uid, sid, "1fd6e28fd158406995f77727b35bf20a")

def get_signature_v2(params, uid=0, sid=''):
    return __get_signature(params, uid, sid, "0C077B1E70F5FDDE6F497C1315687F9C")

'''
params = {
    "username": "1700012608@pku.cn",
    "pwd": MD5("123456").upper(),
    "timestamp": 1538184320,
}

uid = 0
sid = ''

signature1 = "B8944CC8E1A8AD57D1837C1AB907D22A"
signature2 = "35F83E7160D426463C20D712CDFC05A6"
'''

'''
params = {
    "touid": 87808183,
    "option": "info",
    "timestamp": 1538184324,
}

uid = 87808183
sid = "c96db474470a06b3335490d2331d5f5d"

signature1 = "225F10B94560F337EA27F1BFA576ACC0"
signature2 = "098F5D924BC82C040B26A8F05F75A22D"
'''

'''
for item in permutations([userName[:userName.rfind(".")].lower(), password, timestamp]):
    sn = MD5("raowenyuan" + "".join(item)).upper()
    print(sn, sn == signature)
'''

'''
sn1 = get_signature_v1(params, uid, sid)
sn2 = get_signature_v2(params, uid, sid)
print(sn1, sn1 == signature1)
print(sn2, sn2 == signature2)

out = quote("sid=%suid=%s" % (sid, uid))
print(out)
'''

def loginUrlSign(path, dateline, lasttime, second, meter):
    str1 = path[:path.index('.')] if '.' in path else path
    str2 = str(dateline)
    str3 = "{}{}{}".format(lasttime, second, meter)
    print(str1, str2, str3)
    str0 = "raowenyuan{}joy{}the{}run".format(str1.lower(), str2, str3.lower())
    return MD5(str0).lower()

def loginUrlSign(path, dateline, strAry):
    return MD5("raowenyuan{path}joy{timestamp}the{keys}run".format(
            path = path[:path.index('.')].lower() if '.' in path else path.lower(),
            timestamp = str(dateline),
            keys = "".join(map(str, strAry)),
        ))

path = "po.aspx"
dateline = 1538284879
lasttime = 1538284877
second = 1298
meter = 1546

signature = "e4b8e9359e86247954f831cea60abc75"

sn = loginUrlSign(path, dateline, [lasttime, second, meter])
print(sn, sn == signature)

