#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: util/class_.py
#
# 通用类库
#

import os
import sys
from configparser import RawConfigParser
import logging


basedir = os.path.join(os.path.dirname(__file__), "../")


__all__ = [
    "Config",
    "Logger",
]


class Config(object):
    """ [配置文件类，configparser 模块的封装]

        Attributes:
            class:
                Config_File    str                配置文件绝对路径
            instance:
                __config       RawConfigParser    RawConfigParser 类实例
    """
    Config_File = os.path.abspath(os.path.join(basedir, "config.ini"))

    def __init__(self):
        self.__config = RawConfigParser(allow_no_value=True)
        self.__config.read(self.Config_File, encoding="utf-8") # 需要指明 encoding 避免不同系统默认编码不同导致乱码

    def __getitem__(self, idx):
        """ config[] 操作运算的封装
        """
        return self.__config[idx]

    def sections(self):
        """ config.sections 函数的封装
        """
        return self.__config.sections()

    def __get(self, get_fn, section, key, **kwargs):
        """ 配置文件 get 函数模板

            Args:
                get_fn     function    原始的 config.get 函数
                section    str         section 名称
                key        str         section 下的 option 名称
                **kwargs               传入 get_fn
            Returns:
                value      str/int/float/bool   返回相应 section 下相应 key 的 value 值
        """
        value = get_fn(section, key, **kwargs)
        if value is None:
            raise ValueError("key '%s' in section [%s] is missing !" % (key, section))
        else:
            return value

    """
        以下对四个 config.get 函数进行封装

        Args:
            section    str    section 名称
            key        str    section 下的 option 名称
        Returns:
            value             以特定类型返回相应 section 下相应 key 的 value 值
    """
    def get(self, section, key):
        return self.__get(self.__config.get, section, key)

    def getint(self, section, key):
        return self.__get(self.__config.getint, section, key)

    def getfloat(self, section, key):
        return self.__get(self.__config.getfloat, section, key)

    def getboolean(self, section, key):
        return self.__get(self.__config.getboolean, section, key)


class Logger(object):
    """ [日志类，logging 模块的封装]

        Attributes:
            class:
                Default_Name     str                    缺省的日志名
                config           Config                 配置文件类实例
            instance:
                logger           logging.Logger         logging 的 Logger 对象
                level            int                    logging.level 级别
                format           logging.Formatter      日志格式
                console_headler  logging.StreamHandler  控制台日志 handler
    """
    Default_Name = __name__
    config = Config()

    def __init__(self, name=None):
        self.logger = logging.getLogger(name or self.Default_Name)
        self.level = logging.DEBUG if self.config.getboolean("Base", "debug") else logging.INFO
        self.logger.setLevel(self.level)
        self.add_handler(self.console_headler)

    @property
    def format(self):
        fmt = ("[%(levelname)s] %(name)s, %(asctime)s, %(message)s", "%Y-%m-%d %H:%M:%S")
        return logging.Formatter(*fmt)

    @property
    def console_headler(self):
        console_headler = logging.StreamHandler(sys.stdout)
        console_headler.setLevel(self.level)
        console_headler.setFormatter(self.format)
        return console_headler

    def add_handler(self, handler):
        """ logging.addHander 函数的封装，非重复地添加 handler

            Args:
                handler    logging.Handler    logging 的 Handler 对象
            Returns:
                None
        """
        for hd in self.logger.handlers:
            if hd.__class__.__name__ == handler.__class__.__name__:
                return # 不重复添加
        self.logger.addHandler(handler)

    """
        以下是对 logging 的五种 level 输出函数的封装
        并定义 __call__ = logging.info
    """
    def debug(self, *args, **kwargs):
        return self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        return self.logger.critical(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.info(*args, **kwargs)