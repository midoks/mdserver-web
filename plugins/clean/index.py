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


def getLockFile():
    return getServerDir() + "/installed_lock.pl"


def runLog():
    return getServerDir() + "/clean.log"


def status():
    initConf()
    if os.path.exists(getLockFile()):
        return "start"
    return 'stop'


def initConf():
    conf = getConf()
    if not os.path.exists(conf):
        content = ""

        clog = [
            "/var/log/cron-*",
            "/var/log/maillog-*",
            "/var/log/secure-*",
            "/var/log/spooler-*",
            "/var/log/yum.log-*",
            "/var/log/messages-*",
            "/var/log/btmp-*",
            "/var/log/audit/audit.log.*",
            "/var/log/rhsm/rhsm.log-*",
            "/var/log/rhsm/rhsmcertd.log-*",
            "/tmp/yum_save_*",
            "/tmp/tmp.*",
        ]
        for i in clog:
            content += i + "\n"

         # 常用日志
        clogcom = [
            "/var/log/messages",
            "/var/log/btmp",
            "/var/log/wtmp",
            "/var/log/secure",
            "/var/log/lastlog",
            "/var/log/cron",
            "/www/server/cron"
        ]
        for i in clogcom:
            if os.path.exists(i):
                content += i + "\n"

        # 清理日志
        rootDir = "/var/log"

        l = os.listdir(rootDir)
        for x in range(len(l)):
            abspath = rootDir + "/" + l[x]
            content += abspath + "\n"
        mw.writeFile(conf, content)


def start():
    initConf()

    lock_file = getLockFile()
    if not os.path.exists(lock_file):
        mw.writeFile(lock_file, "")

        import tool_task
        tool_task.createBgTask()
        return 'ok'

    return 'fail'


def stop():
    initConf()
    lock_file = getLockFile()
    if os.path.exists(lock_file):
        os.remove(lock_file)
        import tool_task
        tool_task.removeBgTask()
        return 'ok'

    return 'fail'


def reload():
    return 'ok'


def get_filePath_fileName_fileExt(filename):
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension


def cleanFileLog(path):
    filepath, shotname, extension = get_filePath_fileName_fileExt(path)
    if extension == ".log":
        cmd = "echo \"\" > " + path
        tmp = mw.execShell(cmd)
        if tmp[1] != "":
            cmd += " | error:" + tmp[1].strip()
        print(cmd)


def cleanSelfFileLog(path):
    filepath, shotname, extension = get_filePath_fileName_fileExt(path)
    if extension == ".log":
        cmd = "echo \"\" > " + path
        tmp = mw.execShell(cmd)
        if tmp[1] != "":
            cmd += " | error:" + tmp[1].strip()
        print(cmd)


def cleanDirLog(path):
    l = os.listdir(path)
    for x in range(len(l)):
        abspath = path + "/" + l[x]
        if os.path.isfile(abspath):
            cleanFileLog(abspath)
        if os.path.isdir(abspath):
            cleanDirLog(abspath)


def cleanLog():
    conf = getConf()
    clist = mw.readFile(conf).strip()
    clist = clist.split("\n")

    for x in clist:
        abspath = x.strip()

        if abspath.find('*') > 1:
            cmd = 'rm -rf ' + abspath
            print(cmd)
            data = mw.execShell(cmd)
            # print(data)
            continue

        if os.path.exists(abspath):
            if os.path.isfile(abspath):
                cleanSelfFileLog(abspath)
                continue

            if os.path.isdir(abspath):
                cleanDirLog(abspath)
                continue

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
    elif func == 'run_log':
        print(runLog())
    elif func == 'clean':
        cleanLog()
    else:
        print('error')
