# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import sys
import re
import time
import math
import psutil


import core.mw as mw

# --------------------------------------------  数据查询相关 --------------------------------------------
# 格式化addtime列
def toAddtime(data, tomem=False):
    import time
    if tomem:
        import psutil
        mPre = (psutil.virtual_memory().total / 1024 / 1024) / 100
    length = len(data)
    he = 1
    if length > 100:
        he = 1
    if length > 1000:
        he = 3
    if length > 10000:
        he = 15
    if he == 1:
        for i in range(length):
            data[i]['addtime'] = time.strftime(
                '%m/%d %H:%M', time.localtime(float(data[i]['addtime'])))
            if tomem and data[i]['mem'] > 100:
                data[i]['mem'] = data[i]['mem'] / mPre

        return data
    else:
        count = 0
        tmp = []
        for value in data:
            if count < he:
                count += 1
                continue
            value['addtime'] = time.strftime(
                '%m/%d %H:%M', time.localtime(float(value['addtime'])))
            if tomem and value['mem'] > 100:
                value['mem'] = value['mem'] / mPre
            tmp.append(value)
            count = 0
        return tmp

# 格式化addtime列
def toUseAddtime(data):
    dlen = len(data)
    for i in range(dlen):
        data[i]['addtime'] = time.strftime('%m/%d %H:%M:%S', time.localtime(float(data[i]['addtime'])))
    return data

def getLoadAverageByDB(start, end):
    # 获取系统的负载统计信息
    data = mw.M('load_average').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?", (start, end,))\
        .field('pro,one,five,fifteen,addtime')\
        .order('id asc').select()
    data = toUseAddtime(data)
    return data

def getDiskIoByDB(start, end):
    # 获取系统的磁盘IO统计信息
    data = mw.M('diskio').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?", (start, end))\
        .field('read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime')\
        .order('id asc').select()
    data = toUseAddtime(data)
    return data

def getCpuIoByDB(start, end):
    # 获取系统的CPU/IO统计信息
    data = mw.M('cpuio').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?",(start, end))\
        .field('pro,mem,addtime')\
        .order('id asc').select()
    data = toUseAddtime(data)
    return data

def getNetworkIoByDB(start, end):
    # 获取系统网络IO统计信息
    # id,
    data = mw.M('network').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?", (start, end))\
        .field('up,down,total_up,total_down,down_packets,up_packets,addtime')\
        .order('id asc').select()
    data = toUseAddtime(data)
    return data

# --------------------------------------------  数据查询相关 --------------------------------------------
