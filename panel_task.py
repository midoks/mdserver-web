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

g_log_file = mw.getPanelTaskLog()
isTask = mw.getMWLogs() + '/panelTask.pl'

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

def mw_async(f):
    def wrapper(*args, **kwargs):
        thr = threading.Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

@mw_async
def restartMw():
    time.sleep(1)
    cmd = mw.getPanelDir() + '/scripts/init.d/mw reload &'
    mw.execShell(cmd)


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

        writeLogs('done')
    except Exception as e:
        writeLogs(str(e))
    return True

def downloadHook(count, blockSize, totalSize):
    # 下载文件进度回调
    global pre
    used = count * blockSize
    pre1 = int((100.0 * used / totalSize))
    if pre == (100 - pre1):
        return
    speed = {'total': totalSize, 'used': used, 'pre': pre1}
    writeLogs(json.dumps(speed))

def runPanelTask():
    try:
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
    except Exception as e:
        print(mw.getTracebackInfo())

    # 站点过期检查
    # siteEdate()

# 任务队列
def startPanelTask():
    try:
        while True:
            runPanelTask()
            time.sleep(1)
    except Exception as e:
        print(mw.getTracebackInfo())
        time.sleep(10)
        startPanelTask()

# 网站到期处理
def siteEdate():
    global oldEdate
    try:
        if not oldEdate:
            oldEdate = mw.readFile('data/edate.pl')
        if not oldEdate:
            oldEdate = '0000-00-00'
        mEdate = time.strftime('%Y-%m-%d', time.localtime())
        if oldEdate == mEdate:
            return False
        edateSites = mw.M('sites').where('edate>? AND edate<? AND (status=? OR status=?)',
                                         ('0000-00-00', mEdate, 1, '正在运行')).field('id,name').select()
        import site_api
        for site in edateSites:
            site_api.site_api().stop(site['id'], site['name'])
        oldEdate = mEdate
        mw.writeFile('data/edate.pl', mEdate)
    except Exception as e:
        print(str(e))


def systemTask():
    # 系统监控任务
    from  utils.system import monitor
    try:
        while True:
            monitor.instance().run()
            time.sleep(5)
    except Exception as ex:
        print(mw.getTracebackInfo())
        time.sleep(30)
        systemTask()


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
        pid = sdir + '/php/' + version + '/var/run/php-fpm.pid'
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
        print(mw.getTracebackInfo())
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
    restartTip = mw.getPanelDir()+'/data/restart.pl'
    while True:
        if os.path.exists(restartTip):
            os.remove(restartTip)
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


    # Panel Restart Start
    rps = threading.Thread(target=restartPanelService)
    rps = setDaemon(rps)
    rps.start()

    # 面板后台任务
    startPanelTask()

if __name__ == "__main__":
    run()
    
