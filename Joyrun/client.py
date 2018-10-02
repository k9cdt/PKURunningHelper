#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: Joyrun/client.py

import os
import time
from functools import partial, wraps
import requests
from urllib.parse import quote

try:
    from .auth import JoyrunAuth
    from .record import Record
    from .error import (
            JoyrunRequestStatusError,
            JoyrunRetStateError,
            JoyrunSidInvalidError,
        )
except (ImportError, SystemError, ValueError):
    from auth import JoyrunAuth
    from record import Record
    from error import (
            JoyrunRequestStatusError,
            JoyrunRetStateError,
            JoyrunSidInvalidError,
        )

try:
    from ..util import (
            Config, Logger,
            pretty_json, json_load, json_dump, MD5,
            json, JSONDecodeError,
        )
except (ImportError, SystemError, ValueError):
    import sys
    sys.path.append("../")
    from util import (
            Config, Logger,
            pretty_json, json_load, json_dump, MD5,
            json, JSONDecodeError,
        )


Root_Dir = os.path.join(os.path.dirname(__file__), "../")
Cache_Dir = os.path.join(Root_Dir, "cache/")

json_load = partial(json_load, Cache_Dir)
json_dump = partial(json_dump, Cache_Dir)

config = Config()


__all__ = ["JoyrunClient",]


def sid_invalid_retry(retry=1):
    """ 鉴权失败，一般是因为在手机上登录，导致上次登录的 token 失效。
        该函数用于返回一个函数修饰器，被修饰的 API 函数如果发生鉴权错误，
        则重新登录后重新调用 API 函数，最高 retry 次

        Args:
            retry    int    重新尝试的次数，默认只重试一次
        Raises:
            JoyrunSidInvalidError    超过重复校验次数后仍然鉴权失败
    """
    def func_wrapper(func):
        @wraps(func)
        def return_wrapper(self, *args, **kwargs):
            count = 0
            while True:
                try:
                    return func(self, *args, **kwargs)
                except JoyrunSidInvalidError: # 该错误类捕获 鉴权失败 的异常
                    count += 1
                    if count > retry:
                        break
                    else:
                        self.logger.debug("sid invalid, retry %s" % count)
                        self.login()
                except Exception as err:
                    raise err
            raise JoyrunSidInvalidError("reach retry limit %s" % retry)
        return return_wrapper
    return func_wrapper


class JoyrunClient(object):
    """ Joyrun 悦跑圈客户端类

        Attributes:
            class:
                logger                Logger            日志类实例
                BaseUrl               str               API 基础链接
                Cache_LoginInfo       str               登录状态缓存 json 文件名
            instance:
                userName              str               登录用户名
                password              str               登录密码
                session               request.Session   requests 会话类实例
                auth                  JoyrunAuth        Jourun 请求鉴权类实例
                uid                   int               用户 ID
                sid                   str               会话 ID
                base_headers          dict              基础请求头
                device_info_headers   dict              设备信息请求头
    """
    logger = Logger("joyrun")
    BaseUrl = "https://api.thejoyrun.com"
    Cache_LoginInfo = "Joyrun_LoginInfo.json"


    def __init__(self):
        self.userName = "%s@pku.cn" % config.get("Joyrun", "StudentID")
        self.password = config.get("Joyrun", "Password")

        try:
            cache = json_load(self.Cache_LoginInfo)
        except (FileNotFoundError, JSONDecodeError):
            cache = {}

        self.uid = cache.get("uid", 0)
        self.sid = cache.get("sid", '')

        self.session = requests.Session()

        self.session.headers.update(self.base_headers)
        self.session.headers.update(self.device_info_headers)

        self.auth = JoyrunAuth(self.uid, self.sid)

        if self.uid and self.sid: # 直接从缓存中读取登录状态
            self.__update_loginInfo()
        else:
            self.login() # 否则重新登录


    @property
    def base_headers(self):
        return {
            "Accept-Language": "en_US",
            "User-Agent": "okhttp/3.10.0",
            "Host": "api.thejoyrun.com",
            "Connection": "Keep-Alive",
        }

    @property
    def device_info_headers(self):
        return {
                "MODELTYPE": "Xiaomi MI 5",
                "SYSVERSION": "8.0.0",
                "APPVERSION": "4.2.0",
                "MODELIMEI": "861945034544449",
                "APP_DEV_INFO": "Android#4.2.0#Xiaomi MI 5#8.0.0#861945034544449#%s#xiaomi" % (self.uid or 87808183),
            }

    def __reqeust(self, method, url, **kwargs):
        """ 网路请求函数模板，对返回结果做统一校验

            Args:
                method            str    请求 method
                url               str    请求 url/path
                verify_success    bool   是否校验 success 字段 （默认 true），对于无 success 返回值的请求不需要校验
                **kwargs                 传给 requests.request 函数
            Returns:
                respJson      jsonData   json 数据
            Raises:
                JoyrunRequestStatusError    请求状态码异常
                JoyrunRetStateError         ret 字段非 0 -> 请求结果异常
                JoyrunSidInvalidError       sid 失效，登录状态异常
        """
        if url[:7] != "http://" and url[:8] != "https://":
            url = "{base}/{path}".format(base=self.BaseUrl,
                        path=url[1:] if url[0] == '/' else url) # //user/login/normal 需要保留两个 '/' !

        resp = self.session.request(method, url, **kwargs)
        # self.logger.debug("request.url = %s" % resp.url)
        # self.logger.debug("request.headers = %s" % resp.request.headers)
        # self.logger.debug("request.body = %s" % resp.request.body)
        # self.logger.debug("response.headers = %s" % resp.headers)

        if not resp.ok:
            self.logger.error("request.url = %s" % resp.url)
            self.logger.error("request.headers = %s" % pretty_json(dict(resp.request.headers)))
            self.logger.error("session.cookies = %s" % pretty_json(self.session.cookies.get_dict()))
            if resp.request.method == 'POST':
                self.logger.error("request.body = %s" % resp.request.body)
            self.logger.error("response.text = %s" % resp.text)
            raise JoyrunRequestStatusError("response.ok error")

        respJson = resp.json()
        if respJson.get("ret") != "0":
            if respJson.get("ret") == "401":
                raise JoyrunSidInvalidError("sid invalid")
            else:
                self.logger.error("response.json = %s" % pretty_json(respJson))
                raise JoyrunRetStateError("response.json error")

        self.logger.debug("request.url = %s" % resp.url)
        self.logger.debug("response.json = %s" % pretty_json(respJson))

        return respJson

    def get(self, url, params={}, **kwargs):
        return self.__reqeust('GET', url, params=params, **kwargs)

    def post(self, url, data={}, **kwargs):
        return self.__reqeust('POST', url, data=data, **kwargs)


    def __update_loginInfo(self):
        """ 更新登录状态信息

            更新本地 uid, sid 记录
            更新鉴权实例 uid, sid 记录
            更新 cookies 信息
            更新 headers 设备信息
        """
        self.auth.reload(uid=self.uid, sid=self.sid)
        loginCookie = "sid=%s&uid=%s" % (self.sid, self.uid)
        self.session.headers.update({"ypcookie": loginCookie})
        self.session.cookies.clear()
        self.session.cookies.set("ypcookie", quote(loginCookie).lower())
        self.session.headers.update(self.device_info_headers) # 更新设备信息中的 uid 字段

    def __parse_record(self, respJson):
        """ 解析 get_record 返回的 json 包
        """
        r = respJson["runrecord"]
        r["altitude"] = json.loads(r["altitude"])
        r["heartrate"] = json.loads(r["heartrate"])
        r["stepcontent"] = [[json.loads(y) for y in x] for x in json.loads(r["stepcontent"])]
        r["stepremark"] = json.loads(r["stepremark"])
        r["content"] = [json.loads(x) for x in r["content"].split("-")]
        return respJson


    def get_timestamp(self):
        respJson = self.get("/GetTimestamp.aspx")

    @sid_invalid_retry(1)
    def get_dataMessages(self):
        params = {
                "lasttime": 0,
            }
        respJson = self.get("/dataMessages", params, auth=self.auth.reload(params))

    def login(self):
        """ 登录 API
        """
        params = {
                "username": self.userName,
                "pwd": MD5(self.password).upper(),
            }
        respJson = self.get("//user/login/normal", params, auth=self.auth.reload(params))

        self.sid = respJson['data']['sid']
        self.uid = int(respJson['data']['user']['uid'])

        json_dump(self.Cache_LoginInfo, {"sid": self.sid, "uid": self.uid}) # 缓存新的登录信息
        self.__update_loginInfo()

    def logout(self):
        """ 登出 API
            登出后 sid 仍然不会失效 ！ 可能是闹着玩的 API ...
        """
        respJson = self.post("/logout.aspx", auth=self.auth.reload())

    @sid_invalid_retry(1)
    def get_bindings(self):
        respJson = self.get("//user/getbindings", auth=self.auth.reload())

    @sid_invalid_retry(1)
    def get_myInfo(self):
        """ 获取用户信息 API
        """
        payload = {
                "touid": self.uid,
                "option": "info",
            }
        respJson = self.post("/user.aspx", payload, auth=self.auth.reload(payload))

    @sid_invalid_retry(1)
    def get_myInfo_detail(self):
        payload = {
                "option": "get",
            }
        respJson = self.post("/oneclickdetails.aspx", payload, auth=self.auth.reload(payload))

    @sid_invalid_retry(1)
    def get_friends(self):
        payload = {
                "dateline": 1,
                "option": "friends"
            }
        respJson = self.post("/user.aspx", payload, auth=self.auth.reload(payload))

    @sid_invalid_retry(1)
    def get_feed_messages(self):
        payload = {
                "lasttime": 0,
            }
        respJson = self.post("/feedMessageList.aspx", payload, auth=self.auth.reload(payload))

    @sid_invalid_retry(1)
    def get_feed_remind(self):
        respJson = self.post("/Social/GetFeedRemind.aspx", auth=self.auth.reload())

    @sid_invalid_retry(1)
    def get_records(self):
        """ 获取跑步记录 API
        """
        payload = {
                "year": 0,
            }
        respJson = self.post("/userRunList.aspx", payload, auth=self.auth.reload(payload))

    @sid_invalid_retry(1)
    def get_best_record(self):
        payload = {
                "touid": self.uid,
                "option": "record",
            }
        respJson = self.post("/run/best", payload, auth=self.auth.reload(payload))

    @sid_invalid_retry(1)
    def get_record(self, fid):
        """ 获取跑步单次记录详情 API
        """
        payload = {
                "fid": fid,
                "wgs": 1,
            }
        respJson = self.post("/Run/GetInfo.aspx", payload, auth=self.auth.reload(payload))
        json_dump("record.%s.json" % fid, respJson)
        json_dump("record.%s.parse.json" % fid, self.__parse_record(respJson))

    @sid_invalid_retry(1)
    def upload_record(self, record):
        """ 上传跑步记录
        """
        payload = {
                "altitude": record.altitude,
                "private": 0,
                "dateline": record.dateline,
                "city": "北京",
                "starttime": record.starttime,
                "type": 1,
                "content": record.content,
                "second": record.second,
                "stepcontent": record.stepcontent,
                "province": "北京市",
                "stepremark": record.stepremark,
                "runid": record.runid,
                "sampleinterval": record.sampleinterval,
                "wgs": 1,
                "nomoment": 1,
                "meter": record.meter,
                "heartrate": "[]",
                "totalsteps": record.totalsteps,
                "nodetime": record.nodetime,
                "lasttime": record.lasttime,
                "pausetime": "",
                "timeDistance": record.timeDistance,
            }
        # self.logger.info(pretty_json(payload))
        respJson = self.post("/po.aspx", payload, auth=self.auth.reload(payload))


    def run(self):
        """ 项目主程序外部调用接口
        """
        distance = config.getfloat("Joyrun", "distance") # 总距离 km
        pace = config.getfloat("Joyrun", "pace") # 速度 min/km
        stride_frequncy = config.getint("Joyrun", "stride_frequncy") # 步频 step/min

        record = Record(distance, pace, stride_frequncy)
        self.upload_record(record)


if __name__ == '__main__':
    client = JoyrunClient()

    # client.get_timestamp()
    # client.get_dataMessages()
    # client.login()
    # client.logout()
    # client.get_myInfo()
    # client.get_myInfo_detail()
    # client.get_feed_messages()
    # client.get_feed_remind()
    # client.get_friends()
    # client.get_bindings()
    # client.get_records()
    client.get_best_record()
    # client.get_record(247616368)

