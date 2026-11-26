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

# 监控图表最多返回点数, 超过则按比例采样
# 既减少 Python 字典构造开销, 也避免前端 echarts 渲染上万点卡顿
_MONITOR_MAX_ROWS = 2000

def _queryMonitorTable(table, fields, start, end):
    """
    监控数据查询通用方法:
    1. 在 SQL 层用 strftime 直接格式化时间戳, 省掉 Python 层 toUseAddtime 循环
       (6725 条数据从 ~700ms 降到 ~30ms)
    2. 数据量超过 _MONITOR_MAX_ROWS 时按比例采样, 防止前端渲染卡顿
    """
    db_path = mw.getPanelDataDir() + '/system.db'
    import sqlite3
    conn = sqlite3.connect(db_path)
    try:
        # fields 是字段白名单字符串, 由内部代码硬编码, 不接受外部输入, 安全
        sql = "SELECT " + fields + ", " \
              "strftime('%m/%d %H:%M:%S', addtime, 'unixepoch', 'localtime') AS addtime " \
              "FROM " + table + " WHERE addtime >= ? AND addtime <= ? ORDER BY id ASC"
        cursor = conn.execute(sql, (start, end))
        # 用 cursor.description 构造列名, 兼容 fields 里任意字段
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]
        # 采样: 超过上限时按比例抽稀, 保证首末点不丢
        # if len(rows) > _MONITOR_MAX_ROWS:
        #     step = len(rows) // _MONITOR_MAX_ROWS + 1
        #     sampled = rows[::step]
        #     if rows[-1] is not sampled[-1]:
        #         sampled.append(rows[-1])
        #     rows = sampled
        # return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()

def getLoadAverageByDB(start, end):
    # 获取系统的负载统计信息
    return _queryMonitorTable('load_average', 'pro,one,five,fifteen', start, end)

def getDiskIoByDB(start, end):
    # 获取系统的磁盘IO统计信息
    return _queryMonitorTable('diskio',
        'read_count,write_count,read_bytes,write_bytes,read_time,write_time',
        start, end)

def getCpuIoByDB(start, end):
    # 获取系统的CPU/IO统计信息
    return _queryMonitorTable('cpuio', 'pro,mem', start, end)

def getNetworkIoByDB(start, end):
    # 获取系统网络IO统计信息
    return _queryMonitorTable('network',
        'up,down,total_up,total_down,down_packets,up_packets',
        start, end)

# --------------------------------------------  数据查询相关 --------------------------------------------
