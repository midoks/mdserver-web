# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 计划任务
# ---------------------------------------------------------------------------------

import sys
import os
import json
import time
import threading
import psutil


web_dir = os.getcwd() + "/web"
os.chdir(web_dir)
sys.path.append(web_dir)

import core.mw as mw
import thisdb

from admin import setup
setup.init()

g_log_file = mw.getPanelTaskExecLog()
if not os.path.exists(g_log_file):
    os.system("touch " + g_log_file)

def execShell(cmdstring, cwd=None, timeout=None, shell=True):
    cmd = cmdstring + ' > ' + g_log_file + ' 2>&1'
    return mw.execShell(cmd)

def writeLogs(data):
    # 写输出日志
    try:
        fp = open(g_log_file, 'w+')
        fp.write(data)
        fp.close()
    except:
        pass

def downloadFile(url, filename):
    # 下载文件
    try:
        import urllib
        import socket
        socket.setdefaulttimeout(300)

        headers = ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
        opener = urllib.request.build_opener()
        opener.addheaders = [headers]
        urllib.request.install_opener(opener)

        urllib.request.urlretrieve(url, filename=filename, reporthook=downloadHook)

        if not mw.isAppleSystem():
            os.system('chown www.www ' + filename)

        writeLogs(filename + ' download success!')
    except Exception as e:
        writeLogs(str(e))
    return True

def downloadHook(count, blockSize, totalSize):
    # 下载文件进度回调
    used = count * blockSize
    pre = int((100.0 * used / totalSize))
    speed = {'total': totalSize, 'used': used, 'pre': pre}
    writeLogs(json.dumps(speed))

def runPanelTask():
    # 站点过期检查
    siteEdateCheck()

    lock_file = mw.getTriggerTaskLockFile()
    try:
        if os.path.exists(lock_file):
            bash_list = thisdb.getTaskList(status=-1)
            for task in bash_list:
                thisdb.setTaskStatus(task['id'], 0)

            run_list = thisdb.getTaskList(status=0)
            for run_task in run_list:
                start = int(time.time())
                thisdb.setTaskData(run_task['id'], start=start)
                thisdb.setTaskStatus(run_task['id'], -1)

                if run_task['type'] == 'download':
                    argv = run_task['cmd'].split('|mw|')
                    downloadFile(argv[0], argv[1])
                elif run_task['type'] == 'execshell':
                    execShell(run_task['cmd'])

                end = int(time.time())
                thisdb.setTaskData(run_task['id'], end=end)
                thisdb.setTaskStatus(run_task['id'], 1)

            if thisdb.getTaskUnexecutedCount() < 1:
                os.remove(lock_file)
    except Exception as e:
        print('runPanelTask:',mw.getTracebackInfo())

# 网站到期处理
def siteEdateCheck():
    try:
        from utils.site import sites as MwSites
        website_edate = thisdb.getOption('website_edate', default='0000-00-00')
        now_time_ymd = time.strftime('%Y-%m-%d', time.localtime())

        if website_edate == now_time_ymd:
            return False
        site_list = thisdb.getSitesEdateList(now_time_ymd)
        for site in site_list:
            MwSites.instance().stop(site['id'])
        thisdb.setOption('website_edate', now_time_ymd)
    except Exception as e:
        print('siteEdateCheck:',mw.getTracebackInfo())

# 任务队列
def startPanelTask():
    try:
        while True:
            runPanelTask()
            time.sleep(5)
    except Exception as e:
        print('startPanelTask:',mw.getTracebackInfo())
        time.sleep(30)
        startPanelTask()

def systemTask():
    # 系统监控任务
    from  utils.system import monitor
    try:
        while True:
            monitor_status = thisdb.getOption('monitor_status',type='monitor',default='open')
            if monitor_status == 'open':
                monitor.instance().run()
            time.sleep(5)
    except Exception as ex:
        print('systemTask:',mw.getTracebackInfo())
        time.sleep(30)
        systemTask()


def panelPluginStatusCheck():
    # 系统监控任务
    from  utils.plugin import plugin
    try:
        while True:
            # start_t = time.time()
            plugin.instance().autoCachePluginStatus()
            # end_t = time.time()
            time.sleep(60)
    except Exception as ex:
        print('panelPluginStatusCheck:',mw.getTracebackInfo())
        time.sleep(120)
        panelPluginStatusCheck()

# -------------------------------------- PHP监控 start --------------------------------------------- #
# 502错误检查线程
def check502Task():
    try:
        check_file = mw.getPanelDir() + '/data/502Task.pl'
        while True:
            if os.path.exists(check_file):
                check502()
            time.sleep(10)
    except:
        time.sleep(30)
        check502Task()


def check502():
    try:
        verlist = [
            '52', '53', '54', '55', '56', '70',
            '71', '72', '73', '74', '80', '81', 
            '82', '83', '84'
        ]
        for ver in verlist:
            server_dir = mw.getServerDir()
            php_path = server_dir + '/php/' + ver + '/sbin/php-fpm'
            if not os.path.exists(php_path):
                continue
            if checkPHPVersion(ver):
                continue
            if startPHPVersion(ver):
                print('检测到PHP-' + ver + '处理异常,已自动修复!')
                mw.writeLog('PHP守护程序', '检测到PHP-' + ver + '处理异常,已自动修复!')

    except Exception as e:
        mw.writeLog('PHP守护程序', '自动修复异常:'+str(e))


# 处理指定PHP版本
def startPHPVersion(version):
    server_dir = mw.getServerDir()
    try:
        # system
        phpService = mw.systemdCfgDir() + '/php' + version + '.service'
        if os.path.exists(phpService):
            mw.execShell("systemctl restart php" + version)
            if checkPHPVersion(version):
                return True

        # initd
        fpm = server_dir + '/php/init.d/php' + version
        php_path = server_dir + '/php/' + version + '/sbin/php-fpm'
        if not os.path.exists(php_path):
            if os.path.exists(fpm):
                os.remove(fpm)
            return False

        if not os.path.exists(fpm):
            return False

        # 尝试重载服务
        os.system(fpm + ' reload')
        if checkPHPVersion(version):
            return True
        # 尝试重启服务
        cgi = '/tmp/php-cgi-' + version + '.sock'
        pid = server_dir + '/php/' + version + '/var/run/php-fpm.pid'
        data = mw.execShell("ps -ef | grep php/" + version +" | grep -v grep|grep -v python |awk '{print $2}'")
        if data[0] != '':
            os.system("ps -ef | grep php/" + version + " | grep -v grep|grep -v python |awk '{print $2}' | xargs kill ")
        time.sleep(0.5)
        if not os.path.exists(cgi):
            os.system('rm -f ' + cgi)
        if not os.path.exists(pid):
            os.system('rm -f ' + pid)
        os.system(fpm + ' start')
        if checkPHPVersion(version):
            return True

        # 检查是否正确启动
        if os.path.exists(cgi):
            return True
    except Exception as e:
        print('startPHPVersion:',mw.getTracebackInfo())
        mw.writeLog('PHP守护程序', '自动修复异常:'+str(e))
        return True


def checkPHPVersion(version):
    # 检查指定PHP版本
    try:
        sock = mw.getFpmAddress(version)
        data = mw.requestFcgiPHP(sock, '/phpfpm_status_' + version + '?json')
        result = str(data, encoding='utf-8')
    except Exception as e:
        result = 'Bad Gateway'
    # 检查openresty
    if result.find('Bad Gateway') != -1:
        return False
    if result.find('HTTP Error 404: Not Found') != -1:
        return False

    # 检查Web服务是否启动
    if result.find('Connection refused') != -1:
        return False
    return True

# -------------------------------------- PHP监控 end --------------------------------------------- #


# --------------------------------------OpenResty Auto Restart Start --------------------------------------------- #
# 解决acme.sh续签后,未起效。
def openrestyAutoRestart():
    try:
        while True:
            # 检查是否安装
            odir = mw.getServerDir() + '/openresty'
            if not os.path.exists(odir):
                time.sleep(86400)
                continue
            mw.opWeb('reload')
            time.sleep(86400)
    except Exception as e:
        mw.writeLog('OpenResty检测', '自动修复异常:'+str(e))
        time.sleep(86400)

# --------------------------------------OpenResty Auto Restart End   --------------------------------------------- #

# ------------------------------------  OpenResty Restart At Once Start ------------------------------------------ #


def openrestyRestartAtOnce():
    restart_nginx_tip = mw.getPanelDir()+'/data/restart_nginx.pl'
    while True:
        if os.path.exists(restart_nginx_tip):
            os.remove(restart_nginx_tip)
            mw.opWeb('reload')
        time.sleep(1)
# -----------------------------------   OpenResty Restart At Once End   ------------------------------------------ #


# --------------------------------------Panel Restart Start   --------------------------------------------- #
def restartPanelService():
    restart_tip = mw.getPanelDir()+'/data/restart.pl'
    while True:
        if os.path.exists(restart_tip):
            print("restart panel")
            os.remove(restart_tip)
            mw.panelCmd('restart_panel')
        time.sleep(1)
# --------------------------------------Panel Restart End   --------------------------------------------- #


def setDaemon(t):
    if sys.version_info.major == 3 and sys.version_info.minor >= 10:
        t.daemon = True
    else:
        t.setDaemon(True)
    return t

def run():
    # 系统监控
    sysTask = threading.Thread(target=systemTask)
    sysTask = setDaemon(sysTask)
    sysTask.start()

    # PHP 502错误检查线程
    php502 = threading.Thread(target=check502Task)
    php502 = setDaemon(php502)
    php502.start()

    # OpenResty Restart At Once Start
    oraos = threading.Thread(target=openrestyRestartAtOnce)
    oraos = setDaemon(oraos)
    oraos.start()

    # OpenResty Auto Restart Start
    oar = threading.Thread(target=openrestyAutoRestart)
    oar = setDaemon(oar)
    oar.start()

    # Panel Plugin Status Check
    pps = threading.Thread(target=panelPluginStatusCheck)
    pps = setDaemon(pps)
    pps.start()

    # Panel Restart Start
    rps = threading.Thread(target=restartPanelService)
    rps = setDaemon(rps)
    rps.start()

    # 面板后台任务
    startPanelTask()

if __name__ == "__main__":
    run()
    
