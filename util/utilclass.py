#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: util/utilclass.py

import os
from configparser import RawConfigParser

basedir = os.path.join(os.path.dirname(__file__), "../")


__all__ = [
	"Config",
]


class Config(object):

	Config_File = os.path.abspath(os.path.join(basedir, "config.ini"))

	def __init__(self):
		self.__config = RawConfigParser(allow_no_value=True)
		self.__config.read(self.Config_File)

	def __getitem__(self, idx):
		return self.__config[idx]

	def sections(self):
		return self.__config.sections()

	def __get(self, get_fn, section, key, **kwargs):
		value = get_fn(section, key, **kwargs)
		if value is None:
			raise ValueError("key '%s' in section [%s] is missing !" % (key, section))
		else:
			return value

	def get(self, section, key):
		return self.__get(self.__config.get, section, key)

	def getint(self, section, key):
		return self.__get(self.__config.getint, section, key)

	def getfloat(self, section, key):
		return self.__get(self.__config.getfloat, section, key)

	def getboolean(self, section, key):
		return self.__get(self.__config.getboolean, section, key)

