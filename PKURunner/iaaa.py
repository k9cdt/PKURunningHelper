#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: PKURunner/iaaa.py
#
# iAAA 统一认证客户端
#

import os
import time
import requests
from functools import partial

try:
    from .error import IAAARequestStatusError, IAAASuccessStateError
except (ImportError, SystemError, ValueError):
    from error import IAAARequestStatusError, IAAASuccessStateError

try:
    from ..util import (
            Config, Logger,
            json_load, json_dump, MD5,
            JSONDecodeError,
        )
except (ImportError, SystemError, ValueError):
    import sys
    sys.path.append('../')
    from util import (
            Config, Logger,
            json_load, json_dump, MD5,
            JSONDecodeError
        )


Root_Dir = os.path.join(os.path.dirname(__file__), "../")
Cache_Dir = os.path.join(Root_Dir, "cache/")

json_dump = partial(json_dump, Cache_Dir)
json_load = partial(json_load, Cache_Dir)


__all__ = ["IAAAClient",]


class IAAAClient(object):
    """ IAAA 统一认证类

        Attibutes:
            class:
                AppID                str       PKURunner 在 iaaa 下的 AppID
                AppSecret            str       PKURunner 在 iaaa 下的 SecretKey
                Cache_AccessToken    str       accesstoken 缓存 json 文件名
                Token_Expired        int       token 过期秒数 （此处自定义为 2h）
                logger               Logger    日志类实例
            instance:
                studentID            str       iaaa 认证账号/学号
                password             str       iaaa 认证密码
                headers              dict      基础请求头
    """
    AppID = "PKU_Runner"
    AppSecret = "7696baa1fa4ed9679441764a271e556e" # 或者说 salt

    Cache_AccessToken = "PKURunner_AccessToken.json"
    Token_Expired = 7200 # token 缓存 2 小时

    logger = Logger("PKURunner.IAAA")

    def __init__(self, studentID, password):
        self.studentID = studentID
        self.password = password

    @property
    def headers(self):
        return {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.0.0; MI 5 MIUI/V10.0.1.0.OAACNFH)",
            }

    def __request(self, method, url, raw=False, **kwargs):
        """ 请求函数模板

            Args:
                method    str    请求 method
                url       str    请求 url/path
                raw       bool   是否返回 Response 对象（默认 false），否则返回 json 数据
                **kwargs         传给具体的 requests.request 函数
            Returns:
                respJson    jsonData    json 数据 if raw == False
                resp        Response    原始 Response 实例 if raw == True
            Raises:
                IAAARequestStatusError  请求状态码异常
                IAAASuccessStateError   success 状态为 false
        """
        resp = requests.request(method, url, headers=self.headers, **kwargs)

        if not resp.ok: # 校验 status_code
            self.logger.error(dict(resp.headers))
            raise IAAARequestStatusError("in resp.ok")

        respJson = resp.json() # 校验 success 字段
        if not respJson.get('success'):
            self.logger.error(respJson)
            raise IAAASuccessStateError("in resp.json")

        return respJson if not raw else resp

    def post(self, url, data={}, **kwargs):
        """ requests.post 函数封装
        """
        data["msgAbs"] = self.__get_msgAbs(data) # 添加鉴权字段
        return self.__request('POST', url, data=data, **kwargs)


    def __get_msgAbs(self, payload):
        """ iaaa 鉴权算法
            signature = MD5("&[key1]=[value1]&[key2]=[value2]..." + AppSecret) # key 按字典序排列

            Args:
                payload      dict    post 请求的 payload
            Returns:
                signature    str     签名
        """
        return MD5("&".join("=".join(item) for item in sorted(payload.items())) + self.AppSecret)  # TreeMap 按 keys 升序遍历

    def __login(self):
        """ iaaa 登录 API

            Returns:
                token    str    token 字符串
        """
        respJson = self.post("https://iaaa.pku.edu.cn/iaaa/svc/authen/login.do", {
                "appId": self.AppID,
                "userName": self.studentID,
                "randCode": "",                 # 该字段必须要有
                "password": self.password,
                "smsCode": "SMS",               # 该字段必须要有
                "otpCode": "",                  # 该字段必须要有
            })

        token = respJson.get('token')

        json_dump(self.Cache_AccessToken, {
                "token": token,
                "expire_in": int(time.time()) + self.Token_Expired
            })

        return token

    def get_token(self, refresh=False):
        """ 如果 token 没有过期，则返回缓存 token ，否则重新登录

            Args:
                refresh    bool    是否立即重新登录并刷新缓存（默认 false）
            Returns:
                token      str     token 字符串
        """
        try:
            if refresh:
                token = self.__login()
            else:
                tokenCache = json_load(self.Cache_AccessToken)
                if tokenCache["expire_in"] < time.time():
                    token = self.__login()
                else:
                    token = tokenCache["token"]
        except (FileNotFoundError, JSONDecodeError): # 无缓存文件或者文件为空
            token = self.__login()
        finally:
            return token

    def is_mobile_authen(self):
        """ iaaa 校验是否为手机验证 API
            （这个接口实际上不需要使用）
        """
        respJson = self.post("https://iaaa.pku.edu.cn/iaaa/svc/authen/isMobileAuthen.do", {
                "userName": self.studentID,
                "appId": self.AppID,
            })

        self.logger.info(respJson)

