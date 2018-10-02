#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: PKURunner/client.py
#
# PKURunner 客户端
#

import os
import requests
from requests.auth import AuthBase
from requests_toolbelt import MultipartEncoder
from functools import wraps

try:
    from .iaaa import IAAAClient
    from .record import Record
    from .error import (
            PKURunnerRequestStatusError,
            PKURunnerUnauthorizedError,
            PKURunnerSuccessStateError,
            PKURunnerNotVerifiedError,
        )
except (ImportError, SystemError, ValueError):
    from iaaa import IAAAClient
    from record import Record
    from error import (
            PKURunnerRequestStatusError,
            PKURunnerUnauthorizedError,
            PKURunnerSuccessStateError,
            PKURunnerNotVerifiedError,
        )

try:
    from ..util import (
            Config, Logger,
            pretty_json, json_dump,
            json,
        )
except (ImportError, SystemError, ValueError):
    import sys
    sys.path.append('../')
    from util import (
            Config, Logger,
            pretty_json, json_dump,
            json,
        )


config = Config()


__all__ = ["PKURunnerClient",]


class PKURunnerAuth(AuthBase):
    """ PKURunner 鉴权类
        向每个 headers 内添加 access_token 鉴权字段
    """
    def __init__(self, access_token):
        self.access_token = access_token

    def refresh(self, access_token):
        """ 更新 access_token
        """
        self.access_token = access_token

    def __call__(self, r):
        r.headers["Authorization"] = self.access_token
        return r


def unauthorized_retry(retry=1):
    """ 鉴权失败，一般是因为在手机上登录，导致上次登录的 token 失效。
        该函数用于返回一个函数修饰器，被修饰的 API 函数如果发生鉴权错误，
        则重新登录后重新调用 API 函数，最高 retry 次

        Args:
            retry    int    重新尝试的次数，默认只重试一次
        Raises:
            PKURunnerUnauthorizedError    超过重复校验次数后仍然鉴权失败
    """
    def func_wrapper(func):
        @wraps(func)
        def return_wrapper(self, *args, **kwargs):
            count = 0
            while True:
                try:
                    return func(self, *args, **kwargs)
                except PKURunnerUnauthorizedError: # 该错误类捕获 鉴权失败 的异常
                    count += 1
                    if count > retry:
                        break
                    else:
                        self.logger.debug("token invalid, retry %s" % count)
                        self.login()
                except Exception as err:
                    raise err
            raise PKURunnerUnauthorizedError("reach retry limit %s" % retry)
        return return_wrapper
    return func_wrapper


class PKURunnerClient(object):
    """ PKURunner 客户端类
        封装各种 API 接口

        Attributes:
            class:
                logger           Logger           日志类实例
                BaseUrl          str              服务器 BaseUrl
            instance:
                studentID        str              iaaa 认证账号/学号
                iaaa             IAAAClient       iaaa 认证客户端实例
                access_token     str              iaaa 认证后的 token 字符串
                auth             PKURunnerAuth    PKURunner 客户端鉴权类实例
                headers          dict             基础请求头
    """
    logger = Logger("PKURunner")
    BaseURL = "https://pkunewyouth.pku.edu.cn"


    def __init__(self):
        studentID = config.get("PKURunner", "StudentID")
        password = config.get("PKURunner", "Password")
        self.studentID = studentID
        self.iaaa = IAAAClient(studentID, password)
        self.access_token = self.iaaa.get_token()
        self.auth = PKURunnerAuth(self.access_token)

    @property
    def headers(self):
        return {
                "User-Agent": "okhttp/3.10.0",
            }

    def __request(self, method, url, verify_success=True, **kwargs):
        """ 网路请求函数模板，对返回结果做统一校验

            Args:
                method            str    请求 method
                url               str    请求 url/path
                verify_success    bool   是否校验 success 字段 （默认 true），对于无 success 返回值的请求不需要校验
                **kwargs                 传给 requests.request 函数
            Returns:
                respJson      jsonData   json 数据
            Raises:
                PKURunnerRequestStatusError    请求状态码异常
                PKURunnerUnauthorizedError     鉴权失败
                PKURunnerSuccessStateError     success 状态为 false
        """
        if url[:7] != "http://" and url[:8] != "https://":
            url = "{base}/{path}".format(base=self.BaseURL, path=url.lstrip("/"))

        headers = self.headers
        headers.update(kwargs.pop("headers", {}))

        resp = requests.request(method, url, headers=headers, **kwargs)

        if not resp.ok:
            if resp.text == "Unauthorized":
                raise PKURunnerUnauthorizedError("token invalid")
            else:
                self.logger.error("resp.headers = %s" % pretty_json(dict(resp.headers)))
                self.logger.error("resp.text = %s" % resp.text)
                raise PKURunnerRequestStatusError("resp.ok error")
        else:
            respJson = resp.json()
            if verify_success and not respJson.get("success"):
                self.logger.error(respJson)
                raise PKURunnerSuccessStateError("resp.json error")
            else:
                self.logger.debug("resp.url = {url} \nresp.json = {json}".format(url=resp.url, json=pretty_json(respJson)))
                return respJson

    def get(self, url, params={}, **kwargs):
        return self.__request('GET', url, params=params, **kwargs)

    def post(self, url, data={}, **kwargs):
        return self.__request('POST', url, data=data, **kwargs)


    def login(self):
        """ 用户登录 刷新服务器 token 缓存
        """
        self.access_token = self.iaaa.get_token(refresh=True) # 首先刷新
        self.auth.refresh(self.access_token) # 更新 access_token
        respJson = self.post("user", {
                'access_token': self.access_token,
            })


    def get_latest_version(self):
        """ 获取最新版本号
            public API 无需鉴权
        """
        respJson = self.get("public/client/android/curr_version", verify_success=False)

    def get_latest_version_for_offline(self):
        """ 获取支持离线登录的最新版本
            public API 无需鉴权
        """
        respJson = self.get("https://raw.githubusercontent.com/pku-runner/pku-runner.github.io/android/public/client/android/curr_version", verify_success=False)

    def get_min_version(self):
        """ 获取最低支持版本号
            public API 无需鉴权
        """
        respJson = self.get("public/client/android/min_version", verify_success=False)


    @unauthorized_retry(1)
    def get_records(self):
        """ 获得跑步记录列表
        """
        respJson = self.get("record/{userId}".format(userId=self.studentID), auth=self.auth)

    @unauthorized_retry(1)
    def get_record(self, recordId):
        """ 获得单次跑步记录数据
        """
        respJson = self.get("record/{userId}/{recordId}".format(userId=self.studentID, recordId=recordId), auth=self.auth)
        json_dump("../cache/","record.%s.json" % recordId, respJson)

    @unauthorized_retry(1)
    def get_record_status(self):
        """ 跑步状态总览 （已跑、总里程、起止时间等）
        """
        respJson = self.get("record/status/{userId}".format(userId=self.studentID), auth=self.auth)

    @unauthorized_retry(1)
    def upload_record_without_photo(self, record):
        """ 不带自拍，上传跑步记录
        """
        m = MultipartEncoder(
                fields={
                    'userId': str(self.studentID),
                    'duration': str(record.duration),
                    'date': str(record.date),                        # 后端好像会根据日期来判断是否重复发包
                    'detail': json.dumps(record.detail),             # 路径似乎并不会用来查重
                    'misc': json.dumps({"agent": "Android v1.2+"}),
                    'step': str(record.step),
                }
            )
        # self.logger.debug(record.__dict__)
        # self.logger.debug(m.to_string()) # 注意！ m.to_string() 只能输出一次，第二次将会输出空字节，因此不要用这个方法来调试！
        # return
        respJson = self.post("record/{userId}".format(userId=self.studentID),
            data = m.to_string(), headers = {
                'Content-Type': m.content_type
            }, auth=self.auth)

        if not respJson["data"]["verified"]:
            raise PKURunnerNotVerifiedError("record is not verified, check your running params setting.")


    @unauthorized_retry(1)
    def get_badges(self):
        """ 成就列表/徽章列表
        """
        respJson = self.get("badge/user/{userId}".format(userId=self.studentID), auth=self.auth)


    def get_weather(self):
        """ 获取天气信息
            不需要鉴权
        """
        respJson = self.get("weather/all", verify_success=False)


    def run(self):
        """ 项目主程序外部调用接口
        """
        distance = config.getfloat("PKURunner", "distance") # 总距离 km
        pace = config.getfloat("PKURunner", "pace") # 速度 min/km
        stride_frequncy = config.getint("PKURunner", "stride_frequncy") # 步频 step/min

        record = Record(distance, pace, stride_frequncy)
        self.upload_record_without_photo(record)


if __name__ == '__main__':

    client = PKURunnerClient()

    # client.login()

    # client.get_latest_version()
    # client.get_latest_version_for_offline()
    # client.get_min_version()

    # client.get_records()
    # client.get_record(10)
    # client.get_record_status()

    # client.get_badges()
    # client.get_weather()
