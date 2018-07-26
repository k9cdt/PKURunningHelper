#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: PB/client.py

import os
import gzip
import requests
import time
import random
import copy
from functools import partial

try:
	import simplejson as json
except ModuleNotFoundError:
	import json

try:
	from ..util.utilclass import Config
	from ..util.utilfuncs import json_load
	from ..util.error import AbnormalStateCode
except (ImportError, SystemError, ValueError):
	import sys
	sys.path.append('../')
	from util.utilclass import Config
	from util.utilfuncs import json_load
	from util.error import AbnormalStateCode


datadir = os.path.join(os.path.dirname(__file__), "data/")

json_load = partial(json_load, datadir)


config = Config()


class PBclient(object):

	def __init__(self):
		self.__token = ''
		self.__biggerId = ''


	@property
	def user_agent(self):
		mobile = config.get('Base', 'mobile')
		user_agents = {
			"Android": "Mozilla/5.0 (Linux; U; Android 8.0.0; en-us; MI 5 Build/OPR1.170623.032) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
		}
		if mobile not in user_agents:
			raise ValueError("unregistered mobile type -- %s !" % mobile)
		else:
			return user_agents[mobile]

	@property
	def headers(self):
		return {
			"Accept": "application/json,application/xml,application/xhtml+xml,text/html;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-US,en",
			"User-Agent": self.user_agent,
			"Host": "www.biggerfitness.cn",
		}

	def post(self, url, data={}, **kwargs):
		respJson = requests.post(url, json=data, headers=self.headers, **kwargs).json()
		if respJson.get('state') == 0:
			return respJson.get('data')
		else:
			raise AbnormalStateCode(respJson)


	@property
	def token(self):
		if self.__token != '':
			return self.__token
		else:
			raise ValueError('you should login at first !')

	@token.setter
	def token(self, val):
		self.__token = val

	@property
	def biggerId(self):
		if self.__biggerId != '':
			return self.__biggerId
		else:
			raise ValueError('you should login at first !')

	@biggerId.setter
	def biggerId(self, val):
		self.__biggerId = val


	def login(self):
		data = self.post("http://www.biggerfitness.cn/biggerbuss/account/pkulogin.do",{
			"phone": '', # 手机号选填
			"studentNo": config.get("PB", "StudentID"),
			"pwd": config.get("PB", "Password"),
		})
		self.token = data.get('token')
		self.biggerId = data.get('id')

	def get_record(self):
		return self.post("http://www.biggerfitness.cn/biggerbuss/newtrain/runloglist.do",{
			"id": self.biggerId,
			"token": self.token,
		})

	def get_trainInfo(self, locusId):
		return self.post("http://www.biggerfitness.cn/biggerbuss/newtrain/traininginfo.do",{
			"id": locusId,
			"token": self.token,
		})


	@property
	def running_record(self):

		points_per_loop = json_load("400m.locus.json") # 一圈的坐标
		distance = config.getfloat("PB", "distance") # 总距离 km
		pace = config.getfloat("PB", "pace") # 速度 min/km
		stride_frequncy = config.getint("PB", "stride_frequncy") # 步频 步/min
		duration = distance * pace * 60 # 用时 s

		cal_per_loop = lambda: 20 + random.random() * (23 - 20) # 20-23 每圈
		point_delta = lambda: (random.random() - 0.5) * 0.00005 # 随机坐标偏差
		distance_delta_rate = lambda: 1 + (random.random() - 0.5) * 0.1 # 0.95 - 1.05 的距离随机倍率
		stride_frequncy_delta = lambda: int((random.random() - 0.5) * 2 * 10) # 10步/min 的随机步频偏差
		random_alt = lambda: round(42 + random.random() * (48 - 42), 1) # 42-48 海拔
		random_speed = lambda: round(3.1 + random.random() * (4.4 - 3.1), 2) # 没搞懂 speed 怎么定义的 ...

		def locus_generator():
			end_time = int(time.time() * 1000)
			start_time = now_time = end_time - int(duration * 1000) # 从开始时间起
			now_stepcount = 0
			now_distance = 0.00
			while now_time <= end_time:
				for point in points_per_loop:
					per_distance = 0.4 / len(points_per_loop) * distance_delta_rate() # 两点间距离 km
					now_stepcount += int((stride_frequncy + stride_frequncy_delta()) * per_distance * pace)
					now_distance += per_distance
					yield {
						# "id": ??? # 拿不到主键，但是不加主键也可以提交成功，数据库应该设置了主键自增长
						"alt": random_alt(),
						"speed": random_speed(),
						"heartrate": 0,
						"distance": now_distance,
						"lat": round(point['lat'] + point_delta(), 8),
						"lng": round(point['lng'] + point_delta(), 8),
						"stepcount": now_stepcount,
						"traintime": now_time,
					}
					now_time += int(per_distance * pace * 60 * 1000) # 时间间隔 ms

		locuslist = list(locus_generator())
		distance = locuslist[-1]['distance'] # 实际的距离 km
		duration = (locuslist[-1]['traintime'] - locuslist[0]['traintime']) / 1000 # 实际的用时 s

		return json.dumps({
			"biggerId": self.biggerId,
			"token": self.token,
			"locusrlist": [{
				"cal": int(cal_per_loop() * distance * 1000 / 400),
				"distance": round(distance, 2),
				"duration": int(duration),
				"heartrate": 0,
				"team": 1,
				# "pace": ??? # 此处的 pace 与跑步记录中的 pace 含义不统一
				# "intermittent": ???
				"locuslist": [locuslist],
			}],
		}).encode('utf-8')


	def upload_record(self, data):
		return self.post("http://www.biggerfitness.cn/biggerbuss/newtrain/andfreetrainingzip.do",files={
			'file': gzip.compress(data if isinstance(data, bytes) else data.encode('utf-8'))
		})


	def run(self):
		self.login()
		try:
			data = self.upload_record(self.running_record)
		except AbnormalStateCode as err:
			print("Upload record failed !")
			raise err
		else:
			print("Upload record successfully !")
		finally:
			return data

