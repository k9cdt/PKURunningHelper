#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: Joyrun/auth.py


import time
from requests.auth import AuthBase

try:
    from ..util import (
            Logger,
            MD5,
        )
except (ImportError, SystemError, ValueError):
    import sys
    sys.path.append("../")
    from util import (
            Logger,
            MD5,
        )


__all__ = ["JoyrunAuth",]


class JoyrunAuth(AuthBase):
    """ Joyrun 请求鉴权类

        Attibutes:
            class:
                logger        Logger    日志类实例
            Attributes:
                params        dict      请求参数
                uid           int       用户 ID
                sid           str       会话 ID
    """
    logger = Logger("joyrun.auth")


    def __init__(self, uid=0, sid=''):
        self.params = {}
        self.uid = uid
        self.sid = sid

    def reload(self, params={}, uid=0, sid=''):
        """ 重新设置 params, uid, sid

            Returns:
                self    JoyrunAuth    返回本身，马上用于鉴权
        """
        self.params = params
        if uid and sid:
            self.uid = uid
            self.sid = sid
        return self


    @classmethod
    def __get_signature(cls, params, uid, sid, salt):
        """ 两个通用 signature 的函数模板
        """
        if not uid: # uid == 0 or ''
            uid = sid = ''
        preHashString = "{paramsString}{salt}{uid}{sid}".format(
                paramsString = "".join("".join((k, str(v))) for k, v in sorted(params.items())),
                salt = salt,
                uid = str(uid),
                sid = sid,
            )
        # cls.logger.debug(preHashString)
        return MD5(preHashString).upper()

    @classmethod
    def get_signature_v1(cls, params, uid=0, sid=''):
        """ signature V1
            放在请求参数里
        """
        return cls.__get_signature(params, uid, sid, "1fd6e28fd158406995f77727b35bf20a")

    @classmethod
    def get_signature_v2(cls, params, uid=0, sid=''):
        """ signature V2
            放在请求头里
        """
        return cls.__get_signature(params, uid, sid, "0C077B1E70F5FDDE6F497C1315687F9C")

    @classmethod
    def login_url_sign(cls, path, dateline, strAry):
        """ loginUrlSign 用于上传记录
            描述了请求 url 的 path，请求时间，关键请求参数

            Args:
                path        str     请求路径
                dateline    int     类似与时间戳
                strAry      list    关键请求参数
        """
        return MD5("raowenyuan{path}joy{timestamp}the{keys}run".format(
                path = path[:path.index('.')].lower() if '.' in path else path.lower(),
                timestamp = str(dateline),
                keys = "".join(map(str, strAry)).lower(),
            )).lower()

    @classmethod
    def upload_signature(cls, path, dateline, lasttime, second, meter, **kwargs):
        """ 生成上传记录是的 sign 字段，对 loginUrlSign 的封装

            Args:
                path        str    请求路径
                dateline    int    类似于时间戳
                lasttime    int    结束时间
                second      int    跑步时间
                meter       int    跑步距离
                **kwargs           其他不需要的记录信息
        """
        return cls.login_url_sign(path, dateline, [lasttime, second, meter])


    def __call__(self, r):

        params = self.params.copy()

        if r.method == 'POST' and r.path_url.lstrip('/') == "po.aspx":
            params["sign"] = self.upload_signature(r.path_url.lstrip('/'), **params)

        params["timestamp"] = int(time.time()) # 先加入 timestamp

        signV1 = self.get_signature_v1(params, self.uid, self.sid)
        signV2 = self.get_signature_v2(params, self.uid, self.sid)

        r.headers["_sign"] = signV2 # headers 内还有一鉴权 !

        if r.method == 'GET':
            r.prepare_url(r.url, params={"signature": signV1, "timestamp": params["timestamp"]})
        elif r.method == "POST":
            params["signature"] = signV1
            r.prepare_body(data=params, files=None)

        return r