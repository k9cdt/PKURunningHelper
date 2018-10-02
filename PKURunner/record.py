#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: PKURunner/record.py
#
# 跑步记录类
#

import os
import time
import random
import math
from functools import partial

try:
    from ..util import json_load
except (ImportError, SystemError, ValueError):
    import sys
    sys.path.append('../')
    from util import json_load


Work_Dir = os.path.join(os.path.dirname(__file__)) # 当前工作路径
Data_Dir = os.path.join(Work_Dir, "data/")

json_load = partial(json_load, Data_Dir)


__all__ = ["Record",]


class Record(object):
    """ 54 跑步记录类

        Attibutes:
            class:
                A_Loop_GPS_JSON     str      54 一圈的 GPS 数据
                Distance_Per_Loop   float    实际上传后的每圈距离
            instance:
                duration            int      总跑步时间/s
                date                str      结束时间（时间戳）
                step                int      总步数
                detail              list     跑步路径 GPS 数据， 1 point/s （一秒一个点）
                distance            float    跑步距离/km
                pace                float    跑步速度/(min/km)
                stride_frequncy     int      步频/(step/min)
    """
    A_Loop_GPS_JSON = "400m.250p.54.pkurunner.json"
    Distance_Per_Loop = 0.45 # 由于引入坐标偏移，最终上传后一圈的距离将大于 0.4 km ，此处用于修正上传值与理论值间的误差

    def __init__(self, distance, pace, stride_frequncy):
        """ 由距离、速度、步频来生成一次跑步记录

            Args:
                distance           float   跑步距离/km
                pace               float   跑步速度/(min/km)
                stride_frequncy    int     步频/(step/min)
        """
        self.duration = 0
        self.date = ''
        self.step = 0
        self.detail = []

        self.distance = distance
        self.pace = pace
        self.stride_frequncy = stride_frequncy

        self.__build()


    def __get_date(self):
        """ 获得时间戳
            格式 "2018-09-27T08:04:50.000Z"
        """
        return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

    def __point_delta(self):
        """ 坐标随机偏移量
        """
        return (random.random() - 0.5) * 2 * 0.000015 # 0.000015

    def __pace_delta(self):
        """ 速度随机偏移量
        """
        return (random.random() - 0.5) * 2 * 0.1 # 0.1 min/km

    def __stride_frequncy_delta(self):
        """ 步频随机偏移量
        """
        return int((random.random() - 0.5) * 2 * 15) # 15 step/min


    def __point_generator(self, points_per_loop):
        """ 生成 detail 路径点序列
        """
        points_num_per_loop = int(0.4 * self.pace * 60) # 每圈速度 s/(400m) ，1p/1s 因此每圈秒数等于每圈点数

        if points_num_per_loop > len(points_per_loop): # 确保 250 个点足够描述一圈
            raise ValueError("'pace' should be more than %.2f (min/km) !" % (len(points_per_loop) / 0.4 / 60))

        total_loop = self.distance / 0.4 # 以距离决定循环结束点
        current_loop = 0.0

        while current_loop < total_loop:

            points_num_per_loop = int(0.4 * (self.pace + self.__pace_delta()) * 60) # 每圈引入一个速率偏移量
            for i in range(points_num_per_loop):
                idx = math.floor(i / points_num_per_loop * len(points_per_loop))
                point = points_per_loop[idx].copy() # 一定要调用 copy 否则容易偏移过大
                point[0] += self.__point_delta()
                point[1] += self.__point_delta()
                yield point

                current_loop += (1 / points_num_per_loop)
                if current_loop >= total_loop:
                    break


    def __build(self):
        """ 构造记录
        """
        points_per_loop = json_load(self.A_Loop_GPS_JSON)

        self.date = self.__get_date()
        self.duration = int(self.distance * self.Distance_Per_Loop / 0.4 * (self.pace + self.__pace_delta()) * 60) # 跑步时间/s
        self.step = int((self.stride_frequncy + self.__stride_frequncy_delta()) * self.duration / 60) # 总步数
        self.detail = list(self.__point_generator(points_per_loop))
