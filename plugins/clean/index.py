# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'clean'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/clean.conf"
    return path


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def status():
    if os.path.exists(getConf()):
        return "start"
    return 'stop'


def start():
    file = initDreplace()
    data = mw.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    file = initDreplace()
    data = mw.execShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = mw.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def get_filePath_fileName_fileExt(filename):
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def cleanFileLog(path):
    filepath, shotname, extension = get_filePath_fileName_fileExt(path)
    if extension == ".log":
        cmd = "echo \"\" > " + path
        print(cmd)
        print(mw.execShell(cmd))


def cleanSelfFileLog(path):
    filepath, shotname, extension = get_filePath_fileName_fileExt(path)
    cmd = "echo \"\" > " + path
    print(cmd)
    print(mw.execShell(cmd))


def cleanDirLog(path):
    l = os.listdir(path)
    for x in range(len(l)):
        abspath = path + "/" + l[x]
        if os.path.isfile(abspath):
            cleanFileLog(abspath)
        if os.path.isdir(abspath):
            cleanDirLog(abspath)


def cleanLog():
    # 清理日志
    rootDir = "/var/log"
    print("clean start")

    clog = [
        "rm -rf /var/log/cron-*",
        "rm -rf /var/log/maillog-*",
        "rm -rf /var/log/secure-*",
        "rm -rf /var/log/spooler-*",
        "rm -rf /var/log/yum.log-*",
        "rm -rf /var/log/messages-*",
        "rm -rf /var/log/btmp-*",
        "rm -rf /var/log/audit/audit.log.*",
        "rm -rf /var/log/rhsm/rhsm.log-*",
        "rm -rf /var/log/rhsm/rhsmcertd.log-*",
        "rm -rf /tmp/yum_save_*",
        "rm -rf /tmp/tmp.*",
    ]

    for i in clog:
        print(i)
        mw.execShell(i)

    # 常用日志
    clogcom = [
        "/var/log/messages",
        "/var/log/btmp",
        "/var/log/wtmp",
        "/var/log/secure",
        "/var/log/lastlog",
        "/var/log/cron",
    ]
    for i in clogcom:
        if os.path.exists(i):
            mw.execShell("echo \"\" > " + i)

    l = os.listdir(rootDir)
    for x in range(len(l)):
        abspath = rootDir + "/" + l[x]
        if os.path.isfile(abspath):
            cleanFileLog(abspath)

        if os.path.isdir(abspath):
            cleanDirLog(abspath)

    print("conf clean")

    confFile = getServerDir()
    # mw.readFile()
    confFile = confFile + "/clean.conf"
    clist = mw.readFile(confFile).strip()
    clist = clist.split("\n")

    for x in clist:
        abspath = x.strip()
        if os.path.exists(abspath):
            if os.path.isfile(abspath):
                cleanSelfFileLog(abspath)

            if os.path.isdir(abspath):
                cleanDirLog(abspath)
    print("conf clean end")

    print("clean end")

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'conf':
        print(getConf())
    elif func == 'clean':
        cleanLog()
    else:
        print('error')
