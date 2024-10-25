# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 核心方法库
# ---------------------------------------------------------------------------------


import os
import sys
import time
import string
import json
import hashlib
import shlex
import datetime
import subprocess
import glob
import base64
import re

from random import Random

def execShell(cmdstring, cwd=None, timeout=None, shell=True):

    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,
                           shell=shell, bufsize=4096, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout：%s" % cmdstring)

    if sys.version_info[0] == 2:
        return sub.communicate()

    data = sub.communicate()
    # python3 fix 返回byte数据
    if isinstance(data[0], bytes):
        t1 = str(data[0], encoding='utf-8')

    if isinstance(data[1], bytes):
        t2 = str(data[1], encoding='utf-8')
    return (t1, t2)


def getTracebackInfo():
    import traceback
    return traceback.format_exc()

def getRunDir():
    return os.getcwd()

def getRootDir():
    return os.path.dirname(getRunDir())

def getPanelDir():
    return getRootDir()

def getFatherDir():
    return os.path.dirname(os.path.dirname(getPanelDir()))

def getPluginDir():
    return getPanelDir() + '/plugins'

def getPanelDataDir():
    return getPanelDir() + '/data'

def getMWLogs():
    return getPanelDir() + '/logs'

def getPanelTmp():
    return getPanelDir() + '/tmp'


def getServerDir():
    return getFatherDir() + '/server'

def getLogsDir():
    return getRunDir() + '/wwwlogs'

def getRandomString(length):
    # 取随机字符串
    rnd_str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    chrlen = len(chars) - 1
    random = Random()
    for i in range(length):
        rnd_str += chars[random.randint(0, chrlen)]
    return rnd_str


def getUniqueId():
    """
    根据时间生成唯一ID
    :return:
    """
    current_time = datetime.datetime.now()
    str_time = current_time.strftime('%Y%m%d%H%M%S%f')[:-3]
    unique_id = "{0}".format(str_time)
    return unique_id

def toSize(size, middle='') -> str:
    """
    字节单位转换
    """
    units = ('b', 'KB', 'MB', 'GB', 'TB')
    s = d[0]
    for u in units:
        if size < 1024:
            return str(round(size, 2)) + middle + u
        size = float(size) / 1024.0
        s = u
    return str(round(size, 2)) + middle + u

def returnData(status, msg, data=None):
    if data == None:
        return {'status': status, 'msg': msg}
    return {'status': status, 'msg': msg, 'data': data}

def returnJson(status, msg, data=None):
    return getJson({'status': status, 'msg': msg, 'data': data})

def readFile(filename):
    # 读文件内容
    try:
        fp = open(filename, 'r')
        fBody = fp.read()
        fp.close()
        return fBody
    except Exception as e:
        # print(e)
        return False

def writeFile(filename, content, mode='w+'):
    # 写文件内容
    try:
        fp = open(filename, mode)
        fp.write(content)
        fp.close()
        return True
    except Exception as e:
        return False

def triggerTask():
    isTask = getPanelDir() + '/tmp/panelTask.pl'
    writeFile(isTask, 'True')


def systemdCfgDir():
    # ubuntu
    cfg_dir = '/lib/systemd/system'
    if os.path.exists(cfg_dir):
        return cfg_dir

    # debian,centos
    cfg_dir = '/usr/lib/systemd/system'
    if os.path.exists(cfg_dir):
        return cfg_dir

    # local test
    return "/tmp"


def formatDate(format="%Y-%m-%d %H:%M:%S", times=None):
    # 格式化指定时间戳
    if not times:
        times = int(time.time())
    time_local = time.localtime(times)
    return time.strftime(format, time_local)


def strfToTime(sdate):
    # 转换时间
    import time
    return time.strftime('%Y-%m-%d', time.strptime(sdate, '%b %d %H:%M:%S %Y %Z'))


def md5(content):
    # 生成MD5
    try:
        m = hashlib.md5()
        m.update(content.encode("utf-8"))
        return m.hexdigest()
    except Exception as ex:
        return False


def getFileMd5(filename):
    # 文件的MD5值
    if not os.path.isfile(filename):
        return False

    myhash = hashlib.md5()
    f = file(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def getClientIp():
    from flask import request
    return request.remote_addr.replace('::ffff:', '')


def getJson(data):
    import json
    return json.dumps(data)

def getObjectByJson(data):
    import json
    return json.loads(data)


def getSslCrt():
    if os.path.exists('/etc/ssl/certs/ca-certificates.crt'):
        return '/etc/ssl/certs/ca-certificates.crt'
    if os.path.exists('/etc/pki/tls/certs/ca-bundle.crt'):
        return '/etc/pki/tls/certs/ca-bundle.crt'
    return ''


def getOs():
    return sys.platform


def getOsName():
    cmd = "cat /etc/*-release | grep PRETTY_NAME |awk -F = '{print $2}' | awk -F '\"' '{print $2}'| awk '{print $1}'"
    data = execShell(cmd)
    return data[0].strip().lower()


def getOsID():
    cmd = "cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F '\"' '{print $2}'"
    data = execShell(cmd)
    return data[0].strip()

# 获取文件权限描述
def getFileStatsDesc(
    filename: str | None = None,
    path: str | None = None,
):
    # print(filename,path)
    filename = filename.replace('//', '/')
    try:
        stat = os.stat(filename)
        accept = str(oct(stat.st_mode)[-3:])
        mtime = str(int(stat.st_mtime))
        user = ''
        try:
            user = str(pwd.getpwuid(stat.st_uid).pw_name)
        except:
            user = str(stat.st_uid)
        size = str(stat.st_size)
        link = ''
        if os.path.islink(filename):
            link = ' -> ' + os.readlink(filename)

        if path:
            tmp_path = (path + '/').replace('//', '/')
            filename = filename.replace(tmp_path, '', 1)

        return filename + ';' + size + ';' + mtime + ';' + accept + ';' + user + ';' + link
    except Exception as e:
        return ';;;;;'

def getFileSuffix(file):
    tmp = file.split('.')
    ext = tmp[len(tmp) - 1]
    return ext

def getPathSuffix(path):
    return os.path.splitext(path)[-1]

def getSqitePrefix():
    WIN = sys.platform.startswith('win')
    if WIN:  # 如果是 Windows 系统，使用三个斜线
        prefix = 'sqlite:///'
    else:  # 否则使用四个斜线
        prefix = 'sqlite:////'
    return prefix

def getCpuType():
    cpuType = ''
    if isAppleSystem():
        cmd = "system_profiler SPHardwareDataType | grep 'Processor Name' | awk -F ':' '{print $2}'"
        cpuinfo = execShell(cmd)
        return cpuinfo[0].strip()

    current_os = getOs()
    if current_os.startswith('freebsd'):
        cmd = "sysctl -a | egrep -i 'hw.model' | awk -F ':' '{print $2}'"
        cpuinfo = execShell(cmd)
        return cpuinfo[0].strip()

    # 取CPU类型
    cpuinfo = open('/proc/cpuinfo', 'r').read()
    rep = "model\\s+name\\s+:\\s+(.+)"
    tmp = re.search(rep, cpuinfo, re.I)
    if tmp:
        cpuType = tmp.groups()[0]
    else:
        cpuinfo = execShell('LANG="en_US.UTF-8" && lscpu')[0]
        rep = "Model\\s+name:\\s+(.+)"
        tmp = re.search(rep, cpuinfo, re.I)
        if tmp:
            cpuType = tmp.groups()[0]
    return cpuType


def getInfo(msg, args=()):
    # 取提示消息
    for i in range(len(args)):
        rep = '{' + str(i + 1) + '}'
        msg = msg.replace(rep, args[i])
    return msg

def getLastLine(path, num, p=1):
    pyVersion = sys.version_info[0]
    try:
        import html
        if not os.path.exists(path):
            return ""
        start_line = (p - 1) * num
        count = start_line + num
        fp = open(path, 'rb')
        buf = ""

        fp.seek(0, 2)
        if fp.read(1) == "\n":
            fp.seek(0, 2)
        data = []
        b = True
        n = 0

        for i in range(count):
            while True:
                newline_pos = str.rfind(str(buf), "\n")
                pos = fp.tell()
                if newline_pos != -1:
                    if n >= start_line:
                        line = buf[newline_pos + 1:]
                        try:
                            data.insert(0, html.escape(line))
                        except Exception as e:
                            pass
                    buf = buf[:newline_pos]
                    n += 1
                    break
                else:
                    if pos == 0:
                        b = False
                        break
                    to_read = min(4096, pos)
                    fp.seek(-to_read, 1)
                    t_buf = fp.read(to_read)
                    if pyVersion == 3:
                        if type(t_buf) == bytes:
                            t_buf = t_buf.decode("utf-8", "ignore").strip()
                    buf = t_buf + buf
                    fp.seek(-to_read, 1)
                    if pos - to_read == 0:
                        buf = "\n" + buf
            if not b:
                break
        fp.close()
    except Exception as e:
        return str(e)

    return "\n".join(data)

def getPage(args, result='1,2,3,4,5,8'):
    data = getPageObject(args, result)
    return data[0]


def getPageObject(args, result='1,2,3,4,5,8'):
    # 取分页
    from utils import page
    # 实例化分页类
    page = page.Page()
    info = {}

    info['count'] = 0
    if 'count' in args:
        info['count'] = int(args['count'])

    info['row'] = 10
    if 'row' in args:
        info['row'] = int(args['row'])

    info['p'] = 1
    if 'p' in args:
        info['p'] = int(args['p'])
    info['uri'] = {}
    info['return_js'] = ''
    if 'tojs' in args:
        info['return_js'] = args['tojs']

    if 'args_tpl' in args:
        info['args_tpl'] = args['args_tpl']

    return (page.GetPage(info, result), page)

def isAppleSystem():
    if getOs() == 'darwin':
        return True
    return False

def isDocker():
    return os.path.exists('/.dockerenv')

def isSupportSystemctl():
    if isAppleSystem():
        return False
    if isDocker():
        return False

    current_os = getOs()
    if current_os.startswith("freebsd"):
        return False
    return True

def isDebugMode():
    if isAppleSystem():
        return True

    debugPath = getPanelDir() + "/data/debug.pl"
    if os.path.exists(debugPath):
        return True

    return False

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def writeLog(stype, msg, args=()):
    # 写日志
    uid = 1
    try:
        from flask import session
        if 'uid' in session:
            uid = session['uid']
    except Exception as e:
        print(str(e))
        # pass
        # writeFileLog(getTracebackInfo())
    return writeDbLog(stype, msg, args, uid)

def writeDbLog(stype, msg, args=(), uid=1):
    try:
        import admin.model.logs as logs
        format_msg = getInfo(msg, args)
        logs.add(stype, format_msg, uid)
        # mdate = time.strftime('%Y-%m-%d %X', time.localtime())
        return True
    except Exception as e:
        print("writeDbLog:"+str(e))
        return False


# ---------------------------------------------------------------------------------
# 打印相关 START
# ---------------------------------------------------------------------------------

def echoStart(tag):
    print("=" * 89)
    print("★开始{}[{}]".format(tag, formatDate()))
    print("=" * 89)


def echoEnd(tag):
    print("=" * 89)
    print("☆{}完成[{}]".format(tag, formatDate()))
    print("=" * 89)
    print("\n")


def echoInfo(msg):
    print("|-{}".format(msg))

# ---------------------------------------------------------------------------------
# 打印相关 END
# ---------------------------------------------------------------------------------

