# coding: utf-8

import psutil
import time
import os
import re
import math


import public
from flask import Flask, session


class system_api:
    setupPath = None
    pids = None

    def __init__(self):
        self.setupPath = '/www/server'

    # 名取PID
    def getPid(self, pname):
        try:
            if not self.pids:
                self.pids = psutil.pids()
            for pid in self.pids:
                if psutil.Process(pid).name() == pname:
                    return True
            return False
        except:
            return False

    # 检测指定进程是否存活
    def checkProcess(self, pid):
        try:
            if not self.pids:
                self.pids = psutil.pids()
            if int(pid) in self.pids:
                return True
            return False
        except:
            return False

    def getPanelInfo(self, get=None):
        # 取面板配置
        address = public.GetLocalIp()
        try:
            try:
                port = web.ctx.host.split(':')[1]
            except:
                port = public.readFile('data/port.pl')
        except:
            port = '8888'
        domain = ''
        if os.path.exists('data/domain.conf'):
            domain = public.readFile('data/domain.conf')

        autoUpdate = ''
        if os.path.exists('data/autoUpdate.pl'):
            autoUpdate = 'checked'
        limitip = ''
        if os.path.exists('data/limitip.conf'):
            limitip = public.readFile('data/limitip.conf')

        templates = []
        for template in os.listdir('templates/'):
            if os.path.isdir('templates/' + template):
                templates.append(template)
        template = public.readFile('data/templates.pl')

        check502 = ''
        if os.path.exists('data/502Task.pl'):
            check502 = 'checked'
        return {'port': port, 'address': address, 'domain': domain, 'auto': autoUpdate, '502': check502, 'limitip': limitip, 'templates': templates, 'template': template}

    def getSystemTotal(self, interval=1):
        # 取系统统计信息
        data = self.getMemInfo()
        cpu = self.getCpuInfo(interval)
        data['cpuNum'] = cpu[1]
        data['cpuRealUsed'] = cpu[0]
        data['time'] = self.getBootTime()
        data['system'] = self.getSystemVersion()
        data['isuser'] = public.M('users').where(
            'username=?', ('admin',)).count()
        data['version'] = '0.0.1'
        return data

    def getLoadAverage(self, get=None):
        c = os.getloadavg()
        data = {}
        data['one'] = float(c[0])
        data['five'] = float(c[1])
        data['fifteen'] = float(c[2])
        data['max'] = psutil.cpu_count() * 2
        data['limit'] = data['max']
        data['safe'] = data['max'] * 0.75
        return data

    def getAllInfo(self, get):
        data = {}
        data['load_average'] = self.GetLoadAverage(get)
        data['title'] = self.GetTitle()
        data['network'] = self.GetNetWorkApi(get)
        data['panel_status'] = not os.path.exists(
            '/www/server/panel/data/close.pl')
        import firewalls
        ssh_info = firewalls.firewalls().GetSshInfo(None)
        data['enable_ssh_status'] = ssh_info['status']
        data['disable_ping_status'] = not ssh_info['ping']
        data['time'] = self.GetBootTime()
        # data['system'] = self.GetSystemVersion();
        # data['mem'] = self.GetMemInfo();
        data['version'] = web.ctx.session.version
        return data

    def getTitle(self):
        titlePl = 'data/title.pl'
        title = '宝塔Linux面板'
        if os.path.exists(titlePl):
            title = public.readFile(titlePl).strip()
        return title

    def getSystemVersion(self):
        # 取操作系统版本
        os = public.getOs()
        if os == 'darwin':
            data = public.execShell('sw_vers')[0]
            data_list = data.strip().split("\n")
            mac_version = ''
            for x in data_list:
                mac_version += x.split("\t")[1] + ' '
            return mac_version

        version = public.readFile('/etc/redhat-release')
        if not version:
            version = public.readFile(
                '/etc/issue').strip().split("\n")[0].replace('\\n', '').replace('\l', '').strip()
        else:
            version = version.replace('release ', '').strip()
        return version

    def getBootTime(self):
        # 取系统启动时间
        start_time = psutil.boot_time()
        run_time = time.time() - start_time
        # conf = public.readFile('/proc/uptime').split()
        tStr = float(run_time)
        min = tStr / 60
        hours = min / 60
        days = math.floor(hours / 24)
        hours = math.floor(hours - (days * 24))
        min = math.floor(min - (days * 60 * 24) - (hours * 60))
        return public.getInfo('已不间断运行: {1}天{2}小时{3}分钟', (str(int(days)), str(int(hours)), str(int(min))))

    def getCpuInfo(self, interval=1):
        # 取CPU信息
        cpuCount = psutil.cpu_count()
        used = psutil.cpu_percent(interval=interval)
        return used, cpuCount

    def getMemInfo(self, get=None):
        # 取内存信息
        mem = psutil.virtual_memory()
        if public.getOs() == 'darwin':
            memInfo = {
                'memTotal': mem.total / 1024 / 1024
            }
            memInfo['memRealUsed'] = memInfo['memTotal'] * (mem.percent / 100)
        else:
            memInfo = {
                'memTotal': mem.total / 1024 / 1024,
                'memFree': mem.free / 1024 / 1024,
                'memBuffers': mem.buffers / 1024 / 1024,
                'memCached': mem.cached / 1024 / 1024
            }

            memInfo['memRealUsed'] = memInfo['memTotal'] - \
                memInfo['memFree'] - memInfo['memBuffers'] - \
                memInfo['memCached']
        return memInfo

    def getDiskInfo(self, get=None):
        return self.getDiskInfo2()
        # 取磁盘分区信息
        diskIo = psutil.disk_partitions()
        diskInfo = []

        for disk in diskIo:
            if disk[1] == '/mnt/cdrom':
                continue
            if disk[1] == '/boot':
                continue
            tmp = {}
            tmp['path'] = disk[1]
            tmp['size'] = psutil.disk_usage(disk[1])
            diskInfo.append(tmp)
        return diskInfo

    def getDiskInfo2(self):
        # 取磁盘分区信息
        temp = public.execShell(
            "df -h -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
        tempInodes = public.execShell(
            "df -i -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
        temp1 = temp.split('\n')
        tempInodes1 = tempInodes.split('\n')
        diskInfo = []
        n = 0
        cuts = ['/mnt/cdrom', '/boot', '/boot/efi', '/dev',
                '/dev/shm', '/run/lock', '/run', '/run/shm', '/run/user']
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
            if disk[5] == '/':
                bootLog = os.getcwd() + '/tmp/panelBoot.pl'
                if disk[2].find('M') != -1:
                    if os.path.exists(bootLog):
                        os.system('rm -f ' + bootLog)
                else:
                    if not os.path.exists(bootLog):
                        pass
            if inodes[2] != '0':
                diskInfo.append(arr)
        return diskInfo

    # 清理系统垃圾
    def clearSystem(self, get):
        count = total = 0
        tmp_total, tmp_count = self.ClearMail()
        count += tmp_count
        total += tmp_total
        tmp_total, tmp_count = self.ClearOther()
        count += tmp_count
        total += tmp_total
        return count, total

    # 清理邮件日志
    def clearMail(self):
        rpath = '/var/spool'
        total = count = 0
        import shutil
        con = ['cron', 'anacron', 'mail']
        for d in os.listdir(rpath):
            if d in con:
                continue
            dpath = rpath + '/' + d
            time.sleep(0.2)
            num = size = 0
            for n in os.listdir(dpath):
                filename = dpath + '/' + n
                fsize = os.path.getsize(filename)
                size += fsize
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                print '\t\033[1;32m[OK]\033[0m'
                num += 1
            total += size
            count += num
        return total, count

    # 清理其它
    def clearOther(self):
        clearPath = [
            {'path': '/www/server/panel', 'find': 'testDisk_'},
            {'path': '/www/wwwlogs', 'find': 'log'},
            {'path': '/tmp', 'find': 'panelBoot.pl'},
            {'path': '/www/server/panel/install', 'find': '.rpm'}
        ]

        total = count = 0
        for c in clearPath:
            for d in os.listdir(c['path']):
                if d.find(c['find']) == -1:
                    continue
                filename = c['path'] + '/' + d
                fsize = os.path.getsize(filename)
                total += fsize
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                count += 1
        public.serviceReload()
        os.system('echo > /tmp/panelBoot.pl')
        return total, count

    def getNetWork(self, get=None):
        # return self.GetNetWorkApi(get);
        # 取网络流量信息
        try:
            # 取网络流量信息
            networkIo = psutil.net_io_counters()[:4]
            if not "otime" in session:
                session['up'] = networkIo[0]
                session['down'] = networkIo[1]
                session['otime'] = time.time()

            ntime = time.time()
            networkInfo = {}
            networkInfo['upTotal'] = networkIo[0]
            networkInfo['downTotal'] = networkIo[1]
            networkInfo['up'] = round(float(
                networkIo[0] - session['up']) / 1024 / (ntime - session['otime']), 2)
            networkInfo['down'] = round(
                float(networkIo[1] - session['down']) / 1024 / (ntime - session['otime']), 2)
            networkInfo['downPackets'] = networkIo[3]
            networkInfo['upPackets'] = networkIo[2]

            # print networkIo[1], session['down'], ntime, session['otime']
            session['up'] = networkIo[0]
            session['down'] = networkIo[1]
            session['otime'] = time.time()

            networkInfo['cpu'] = self.getCpuInfo()
            networkInfo['load'] = self.getLoadAverage(get)
            networkInfo['mem'] = self.getMemInfo(get)

            return networkInfo
        except Exception, e:
            return None

    def getNetWorkApi(self, get=None):
        # 取网络流量信息
        try:
            tmpfile = 'data/network.temp'
            networkIo = psutil.net_io_counters()[:4]

            if not os.path.exists(tmpfile):
                public.writeFile(tmpfile, str(
                    networkIo[0]) + '|' + str(networkIo[1]) + '|' + str(int(time.time())))

            lastValue = public.readFile(tmpfile).split('|')

            ntime = time.time()
            networkInfo = {}
            networkInfo['upTotal'] = networkIo[0]
            networkInfo['downTotal'] = networkIo[1]
            networkInfo['up'] = round(
                float(networkIo[0] - int(lastValue[0])) / 1024 / (ntime - int(lastValue[2])), 2)
            networkInfo['down'] = round(
                float(networkIo[1] - int(lastValue[1])) / 1024 / (ntime - int(lastValue[2])), 2)
            networkInfo['downPackets'] = networkIo[3]
            networkInfo['upPackets'] = networkIo[2]

            public.writeFile(tmpfile, str(
                networkIo[0]) + '|' + str(networkIo[1]) + '|' + str(int(time.time())))

            # networkInfo['cpu'] = self.GetCpuInfo(0.1)
            return networkInfo
        except:
            return None

    def restartServer(self, get):
        if not public.IsRestart():
            return public.returnMsg(False, 'EXEC_ERR_TASK')
        public.ExecShell("sync && /etc/init.d/bt stop && init 6 &")
        return public.returnMsg(True, 'SYS_REBOOT')

    # 释放内存
    def reMemory(self, get):
        os.system('sync')
        scriptFile = 'script/rememory.sh'
        if not os.path.exists(scriptFile):
            public.downloadFile(web.ctx.session.home +
                                '/script/rememory.sh', scriptFile)
        public.ExecShell("/bin/bash " + self.setupPath +
                         '/panel/' + scriptFile)
        return self.GetMemInfo()

    # 重启面板
    def reWeb(self, get):
        # if not public.IsRestart(): return
        # public.returnMsg(False,'EXEC_ERR_TASK');
        public.ExecShell('/etc/init.d/bt restart &')
        return True

    # 修复面板
    def repPanel(self, get):
        vp = ''
        if public.readFile('/www/server/panel/class/common.py').find('checkSafe') != -1:
            vp = '_pro'
        public.ExecShell("wget -O update.sh " + public.get_url() +
                         "/install/update" + vp + ".sh && bash update.sh")
        if hasattr(web.ctx.session, 'getCloudPlugin'):
            del(web.ctx.session['getCloudPlugin'])
        return True

    # 升级到专业版
    def updatePro(self, get):
        public.ExecShell("wget -O update.sh " + public.get_url() +
                         "/install/update_pro.sh && bash update.sh pro")
        if hasattr(web.ctx.session, 'getCloudPlugin'):
            del(web.ctx.session['getCloudPlugin'])
        return True
