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
    _netinfo = None

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

    def clearDbFile(self):
        os.remove(self._dbfile)
        self.initDBFile()
        return True

    def initDBFile(self):
        if os.path.exists(self._dbfile):
            return True
        sql_file = mw.getPanelDir() + '/web/admin/setup/sql/system.sql'
        sql = db.Sql().dbPos(mw.getPanelDataDir(),'system')
        csql = mw.readFile(sql_file)
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            sql.execute(csql_list[index], ())
        return True

    def getMonitorDay(self):
        monitor_day = mw.M('option').field('name').where('name=?',('monitor_day',)).getField('value')
        return int(monitor_day)

    def isOnlyNetIoStats(self):
        monitor_only_netio = mw.M('option').field('name').where('name=?',('monitor_only_netio',)).getField('value')
        if monitor_only_netio == 'open':
            return True
        return False

    def psutilNetIoCounters(self):
        '''
        统计网卡流量
        '''
        if self.isOnlyNetIoStats():
            local_lo = (0, 0, 0, 0)
            ioName = psutil.net_io_counters(pernic=True).keys()
            for x in ioName:
                if x.find("lo") > -1:
                    local_lo = psutil.net_io_counters(pernic=True).get(x)[:4]

            all_io = psutil.net_io_counters()[:4]
            result_io = tuple([all_io[i] - local_lo[i] for i in range(0, len(all_io))])

            return result_io
        return psutil.net_io_counters()[:4]

    def getDiskInfo(self):
        now_diskinfo = psutil.disk_io_counters()
        if self._diskinfo is None:
            self._diskinfo = now_diskinfo

        info = {}
        info['read_count'] = now_diskinfo.read_count - self._diskinfo.read_count
        info['write_count'] = now_diskinfo.write_count - self._diskinfo.write_count
        info['read_bytes'] = now_diskinfo.read_bytes - self._diskinfo.read_bytes
        info['write_bytes'] = now_diskinfo.write_bytes - self._diskinfo.write_bytes
        info['read_time'] = now_diskinfo.read_time - self._diskinfo.read_time
        info['write_time'] = now_diskinfo.write_time - self._diskinfo.write_time

        self._diskinfo = now_diskinfo
        return info

    def getNetIoInfo(self):
        # 取当前网络Io
        net_io = self.psutilNetIoCounters()
        if not self._netinfo:
            self._netinfo = net_io
        info = {}
        info['upTotal'] = net_io[0]
        info['downTotal'] = net_io[1]
        info['up'] = round(float((net_io[0] - self._netinfo[0]) / 1024), 2)
        info['down'] = round(float((net_io[1] - self._netinfo[1]) / 1024), 2)
        info['downPackets'] = net_io[3]
        info['upPackets'] = net_io[2]

        self._netinfo = net_io
        return info

    def getLoadAverage(self):
        c = os.getloadavg()
        data = {}
        data['one'] = round(float(c[0]), 2)
        data['five'] = round(float(c[1]), 2)
        data['fifteen'] = round(float(c[2]), 2)
        data['max'] = psutil.cpu_count() * 2
        data['limit'] = data['max']
        data['safe'] = data['max'] * 0.75
        return data

    def run(self):
        self.initDBFile()
        monitor_day = self.getMonitorDay()
        
        info = {}
        # 取当前CPU Io
        info['used'] = psutil.cpu_percent(interval=1)
        info['used'] = round(info['used'], 2)
        
        info['mem'] = getMemUsed()
        info['mem'] = round(info['mem'], 2)

        netio = self.getNetIoInfo()
        diskio = self.getDiskInfo()

        addtime = int(time.time())
        deltime = addtime - (monitor_day * 86400)

        # CPU/内存数据入库
        cpu_mem_data = (info['used'], info['mem'], addtime)
        cmd_objm = mw.M('cpuio').dbPos(mw.getPanelDataDir(),'system')
        cmd_objm.add('pro,mem,addtime', cpu_mem_data)
        cmd_objm.where("addtime<?", (deltime,)).delete()

        # 网络数据入库
        netio_data = (netio['up'] / 5, netio['down'] / 5, netio['upTotal'], netio['downTotal'], netio['downPackets'], netio['upPackets'], addtime)
        network_objm = mw.M('network').dbPos(mw.getPanelDataDir(),'system')
        network_objm.add('up,down,total_up,total_down,down_packets,up_packets,addtime', netio_data)
        network_objm.where("addtime<?", (deltime,)).delete()

        # 磁盘数据入库
        disk_data = (diskio['read_count'], diskio['write_count'], diskio['read_bytes'], diskio['write_bytes'], diskio['read_time'], diskio['write_time'], addtime)
        disk_objm = mw.M('diskio').dbPos(mw.getPanelDataDir(),'system')
        disk_objm.add('read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime', disk_data)
        disk_objm.where("addtime<?", (deltime,)).delete()

        # 负载数据入库
        load_data = self.getLoadAverage()
        lpro = round((load_data['one'] / load_data['max']) * 100, 2)
        if lpro > 100:
            lpro = 100
        load_objm = mw.M('load_average').dbPos(mw.getPanelDataDir(),'system')
        load_objm.add('pro,one,five,fifteen,addtime', (lpro, load_data['one'], load_data['five'], load_data['fifteen'], addtime))
        load_objm.where("addtime<?", (deltime,)).delete()
        return True




