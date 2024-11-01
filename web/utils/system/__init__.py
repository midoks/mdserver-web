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

def getDiskInfo():
    # 取磁盘分区信息
    temp = mw.execShell("df -h -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
    tempInodes = mw.execShell("df -i -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
    temp1 = temp.split('\n')
    tempInodes1 = tempInodes.split('\n')
    diskInfo = []
    n = 0
    cuts = ['/mnt/cdrom', '/boot', '/boot/efi', '/dev',
            '/dev/shm', '/zroot', '/run/lock', '/run', '/run/shm', '/run/user']
    for tmp in temp1:
        n += 1
        inodes = tempInodes1[n - 1].split()
        disk = tmp.split()
        if len(disk) < 5:
            continue
        if disk[1].find('M') != -1:
            continue
        if disk[1].find('K') != -1:
            continue
        if len(disk[5].split('/')) > 4:
            continue
        if disk[5] in cuts:
            continue
        arr = {}
        arr['path'] = disk[5]
        tmp1 = [disk[1], disk[2], disk[3], disk[4]]
        arr['size'] = tmp1
        arr['inodes'] = [inodes[1], inodes[2], inodes[3], inodes[4]]
        diskInfo.append(arr)
    return diskInfo

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



def getLoadAverage():
    c = os.getloadavg()
    data = {}
    data['one'] = round(float(c[0]), 2)
    data['five'] = round(float(c[1]), 2)
    data['fifteen'] = round(float(c[2]), 2)
    data['max'] = psutil.cpu_count() * 2
    data['limit'] = data['max']
    data['safe'] = data['max'] * 0.75
    return data

def getSystemVersion():
    # 取操作系统版本
    current_os = mw.getOs()
    # sys_temper = self.getSystemDeviceTemperature()
    # print(sys_temper)
    # mac
    if current_os == 'darwin':
        data = mw.execShell('sw_vers')[0]
        data_list = data.strip().split("\n")
        mac_version = ''
        for x in data_list:
            xlist = x.split("\t")
            mac_version += xlist[len(xlist)-1] + ' '

        arch_ver = mw.execShell("arch")
        return mac_version + " (" + arch_ver[0].strip() + ")"

    # freebsd
    if current_os.startswith('freebsd'):
        version = mw.execShell(
            "cat /etc/*-release | grep PRETTY_NAME | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")
        arch_ver = mw.execShell(
            "sysctl -a | egrep -i 'hw.machine_arch' | awk -F ':' '{print $2}'")
        return version[0].strip() + " (" + arch_ver[0].strip() + ")"

    redhat_series = '/etc/redhat-release'
    if os.path.exists(redhat_series):
        version = mw.readFile('/etc/redhat-release')
        version = version.replace('release ', '').strip()

        arch_ver = mw.execShell("arch")
        return version + " (" + arch_ver[0].strip() + ")"

    os_series = '/etc/os-release'
    if os.path.exists(os_series):
        version = mw.execShell(
            "cat /etc/*-release | grep PRETTY_NAME | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")

        arch_ver = mw.execShell("arch")
        return version[0].strip() + " (" + arch_ver[0].strip() + ")"

def getBootTime():
    # 取系统启动时间
    uptime = mw.readFile('/proc/uptime')
    if uptime == False:
        start_time = psutil.boot_time()
        run_time = time.time() - start_time
    else:
        run_time = uptime.split()[0]
    tStr = float(run_time)
    min = tStr / 60
    hours = min / 60
    days = math.floor(hours / 24)
    hours = math.floor(hours - (days * 24))
    min = math.floor(min - (days * 60 * 24) - (hours * 60))
    return mw.getInfo('已不间断运行: {1}天{2}小时{3}分钟', (str(int(days)), str(int(hours)), str(int(min))))

def getCpuInfo(interval=1):
    # 取CPU信息
    cpuCount = psutil.cpu_count()
    cpuLogicalNum = psutil.cpu_count(logical=False)
    used = psutil.cpu_percent(interval=interval)
    cpuLogicalNum = 0
    if os.path.exists('/proc/cpuinfo'):
        c_tmp = mw.readFile('/proc/cpuinfo')
        d_tmp = re.findall("physical id.+", c_tmp)
        cpuLogicalNum = len(set(d_tmp))

    used_all = psutil.cpu_percent(percpu=True)
    cpu_name = mw.getCpuType() + " * {}".format(cpuLogicalNum)
    return used, cpuCount, used_all, cpu_name, cpuCount, cpuLogicalNum

def getMemInfo():
    # 取内存信息
    mem = psutil.virtual_memory()
    if sys.platform == 'darwin':
        memInfo = {'memTotal': mem.total}
        memInfo['memRealUsed'] = memInfo['memTotal'] * (mem.percent / 100)
    else:
        memInfo = {
            'memTotal': mem.total,
            'memFree': mem.free,
            'memBuffers': mem.buffers,
            'memCached': mem.cached
        }
        memInfo['memRealUsed'] = memInfo['memTotal'] - memInfo['memFree'] - memInfo['memBuffers'] - memInfo['memCached']
    return memInfo