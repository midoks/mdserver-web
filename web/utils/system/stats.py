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

class stats:
    cache = {}

    # 磁盘统计
    def disk(self):
        iokey = 'disk_stat'
        diskInfo = {}
        diskInfo['ALL'] = {}
        diskInfo['ALL']['read_count'] = 0
        diskInfo['ALL']['write_count'] = 0
        diskInfo['ALL']['read_bytes'] = 0
        diskInfo['ALL']['write_bytes'] = 0
        diskInfo['ALL']['read_time'] = 0
        diskInfo['ALL']['write_time'] = 0
        diskInfo['ALL']['read_merged_count'] = 0
        diskInfo['ALL']['write_merged_count'] = 0

        try:
            diskio = None
            if iokey in self.cache:
                diskio = self.cache[iokey]
            
            mtime = int(time.time())
            if not diskio:
                diskio = {}
                diskio['info'] = None
                diskio['time'] = mtime

            diskio_cache = diskio['info']
            stime = mtime - diskio['time']
            if not stime: stime = 1

            diskio_group = psutil.disk_io_counters(perdisk=True)
            if not diskio_cache:
                diskio_cache = diskio_group
            
            for disk_name in diskio_group.keys():
                diskInfo[disk_name] = {}
                # print('disk_name',disk_name)
                # print(diskio_group[disk_name].write_time , diskio_cache[disk_name].write_time)
                # print(diskio_group[disk_name].write_count , diskio_cache[disk_name].write_count)

                diskInfo[disk_name]['read_count']   = int((diskio_group[disk_name].read_count - diskio_cache[disk_name].read_count) / stime)
                diskInfo[disk_name]['write_count']  = int((diskio_group[disk_name].write_count - diskio_cache[disk_name].write_count) / stime)
                diskInfo[disk_name]['read_bytes']   = int((diskio_group[disk_name].read_bytes - diskio_cache[disk_name].read_bytes) / stime)
                diskInfo[disk_name]['write_bytes']  = int((diskio_group[disk_name].write_bytes - diskio_cache[disk_name].write_bytes) / stime)
                diskInfo[disk_name]['read_time']    = int((diskio_group[disk_name].read_time - diskio_cache[disk_name].read_time) / stime)
                diskInfo[disk_name]['write_time']   = int((diskio_group[disk_name].write_time - diskio_cache[disk_name].write_time) / stime)

                if 'read_merged_count' in diskio_group[disk_name] and 'read_merged_count' in diskio_cache[disk_name]:
                    diskInfo[disk_name]['read_merged_count'] = int((diskio_group[disk_name].read_merged_count - diskio_cache[disk_name].read_merged_count) / stime)
                if 'write_merged_count' in diskio_group[disk_name] and 'write_merged_count' in diskio_cache[disk_name]:
                    diskInfo[disk_name]['write_merged_count'] = int((diskio_group[disk_name].write_merged_count - diskio_cache[disk_name].write_merged_count) / stime)
                
                diskInfo['ALL']['read_count'] += diskInfo[disk_name]['read_count']
                diskInfo['ALL']['write_count'] += diskInfo[disk_name]['write_count']
                diskInfo['ALL']['read_bytes'] += diskInfo[disk_name]['read_bytes']
                diskInfo['ALL']['write_bytes'] += diskInfo[disk_name]['write_bytes']
                if diskInfo['ALL']['read_time'] < diskInfo[disk_name]['read_time']:
                    diskInfo['ALL']['read_time'] = diskInfo[disk_name]['read_time']
                if diskInfo['ALL']['write_time'] < diskInfo[disk_name]['write_time']:
                    diskInfo['ALL']['write_time'] = diskInfo[disk_name]['write_time']

                if 'read_merged_count' in diskInfo[disk_name] and 'read_merged_count' in diskInfo[disk_name]:
                    diskInfo['ALL']['read_merged_count'] += diskInfo[disk_name]['read_merged_count']
                if 'write_merged_count' in diskInfo[disk_name] and 'write_merged_count' in diskInfo[disk_name]:
                    diskInfo['ALL']['write_merged_count'] += diskInfo[disk_name]['write_merged_count']

            self.cache[iokey] = {'info':diskio_group,'time':mtime}
        except Exception as e:
            pass

        return diskInfo

    # 网络统计
    def network(self):
        netInfo = {}

        netInfo['ALL'] = {}
        netInfo['ALL']['up'] = 0
        netInfo['ALL']['down'] = 0
        netInfo['ALL']['upTotal'] = 0
        netInfo['ALL']['downTotal'] = 0
        netInfo['ALL']['upPackets'] = 0
        netInfo['ALL']['downPackets'] = 0

        mtime = time.time()
        iokey = 'net_stat'
        netio = None
        if iokey in self.cache:
            netio = self.cache[iokey]

        if not netio:
            netio = {}
            netio['info'] = None
            netio['all_io'] = None
            netio['time'] = mtime

        stime = mtime - netio['time']
        if not stime: stime = 1

        # print("new:",stime)
        netio_group = psutil.net_io_counters(pernic=True).keys()

        netio_cache = netio['info']
        allio_cache = netio['all_io']
        if not netio_cache:
            netio_cache = {}

        netio_group_t = {}
        for name in netio_group:
            netInfo[name] = {}

            io_data = psutil.net_io_counters(pernic=True).get(name)
            if not name in netio_cache:
                netio_cache[name] = io_data

            netio_group_t[name] = io_data

            netInfo[name]['up'] = round(float((io_data[0] - netio_cache[name][0]) / stime), 2)
            netInfo[name]['down'] = round(float((io_data[1] - netio_cache[name][1])/ stime), 2)

            netInfo[name]['upTotal'] = io_data[0]
            netInfo[name]['downTotal'] = io_data[1]
            netInfo[name]['upPackets'] = io_data[2]
            netInfo[name]['downPackets'] = io_data[3]

        all_io = psutil.net_io_counters()[:4]
        if not allio_cache:
            allio_cache = all_io
        
        netInfo['ALL']['up'] = round(float((all_io[0] - allio_cache[0]) /stime), 2)
        netInfo['ALL']['down'] = round(float((all_io[1] - allio_cache[1]) /stime), 2)
        netInfo['ALL']['upTotal'] = all_io[0]
        netInfo['ALL']['downTotal'] = all_io[1]
        netInfo['ALL']['upPackets'] = all_io[2]
        netInfo['ALL']['downPackets'] = all_io[3]

        self.cache[iokey] = {'info':netio_group_t,'all_io':all_io,'time':mtime}
        return netInfo


