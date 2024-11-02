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
import threading


from .main import getMemUsed

import core.mw as mw
import core.db as db



# 监控系统数据入库
class monitor:

    _dbfile = mw.getPanelDataDir() + '/system.db'
    _diskinfo = None

    def __init__(self):
        pass

    # lock
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(monitor, "_instance"):
            with monitor._instance_lock:
                if not hasattr(monitor, "_instance"):
                    monitor._instance = monitor(*args, **kwargs)
        return monitor._instance

    def initDBFile(self):
        if os.path.exists(self._dbfile):
            return True
        sql_file = mw.getPanelDataDir() + '/sql/system.sql'
        sql = db.Sql().dbPos(mw.getPanelDataDir(),'system')
        csql = mw.readFile(sql_file)
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            sql.execute(csql_list[index], ())
        return True

    # def safeRun(self):
    #     self.initDBFile()

    #     monitor_day =mw.M('option').field('name').where('name=?',('monitor_day',)).getField('value')
    #     print(monitor_day)
    #     print("monitor data", mw.formatDate())

    def getDiskInfo(self):
        if self._diskinfo is None:
            self._diskinfo = psutil.disk_io_counters()

    def run(self):
        self.initDBFile()
        monitor_day = mw.M('option').field('name').where('name=?',('monitor_day',)).getField('value')
        print(monitor_day)
        print("monitor data", mw.formatDate())

        now_info = {}
        # 取当前CPU Io
        now_info['used'] = psutil.cpu_percent(interval=1)
        now_info['mem'] = getMemUsed()

        network_io = psutil.net_io_counters()[:4]
        diskio = psutil.disk_io_counters()

        print(network_io)
        print(now_info)
        print(diskio)
        # if tmp['used'] > 80:
        #     panel_title = mw.getConfig('title')
        #     ip = mw.getHostAddr()
        #     now_time = mw.getDateFromNow()
        #     msg = now_time + '|节点[' + panel_title + ':' + ip + \
        #         ']处于高负载[' + str(tmp['used']) + '],请排查原因!'
        #     mw.notifyMessage(msg, '面板监控', 600)



