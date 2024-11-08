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
    return getFatherDir() + '/wwwlogs'

def getRecycleBinDir():
    rb_dir = getFatherDir() + '/recycle_bin'
    if not os.path.exists(rb_dir):
        os.system('mkdir -p ' + rb_dir)
    return rb_dir

def getPanelTaskLog():
    return getMWLogs() + '/panel_task.log'

def getWwwDir():
    file = getPanelDir() + '/data/site.pl'
    if os.path.exists(file):
        return readFile(file).strip()
    return getFatherDir() + '/wwwroot'


def getPanelPort():
    port_file = getPanelDir()+'/data/port.pl'
    port = readFile(port_file).strip()
    if not port:
        return 7200
    return int(port)

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

def getDate():
    # 取格式时间
    import time
    return time.strftime('%Y-%m-%d %X', time.localtime())


def getDateFromNow(tf_format="%Y-%m-%d %H:%M:%S", time_zone="Asia/Shanghai"):
    # 取格式时间
    import time
    os.environ['TZ'] = time_zone
    time.tzset()
    return time.strftime(tf_format, time.localtime())

def getDataFromInt(val):
    time_format = '%Y-%m-%d %H:%M:%S'
    time_str = time.localtime(val)
    return time.strftime(time_format, time_str)

def getCommonFile():
    # 统一默认配置文件
    base_dir = getPanelDir()+'/'
    data = {
        'debug' : base_dir+'data/debug.pl',                              # DEBUG文件
        'close' : base_dir+'data/close.pl',                              # 识别关闭面板文件
        'basic_auth' : base_dir+'data/basic_auth.json',                  # 面板Basic验证
        'ipv6' : base_dir+'data/ipv6.pl',                                # ipv6识别文件
        'bind_domain' : base_dir+'data/bind_domain.pl',                  # 面板域名绑定
        'auth_secret': base_dir+'data/auth_secret.pl',                   # 二次验证密钥
        'ssl': base_dir+'ssl/choose.pl',                                 # ssl设置
    }
    return data


def toSize(size, middle='') -> str:
    """
    字节单位转换
    """
    units = ('b', 'KB', 'MB', 'GB', 'TB')
    s = units[0]
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
        print(e)
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

def getLocalIp():
    filename = getPanelDir()+'/data/iplist.txt'
    try:
        ipaddress = readFile(filename)
        if not ipaddress or ipaddress == '127.0.0.1':
            cmd = "curl --insecure -4 -sS --connect-timeout 5 -m 60 https://v6r.ipip.net/?format=text"
            ip = execShell(cmd)
            result = ip[0].strip()
            if result == '':
                raise Exception("ipv4 is empty!")
            writeFile(filename, result)
            return result
        return ipaddress
    except Exception as e:
        cmd = "curl --insecure -6 -sS --connect-timeout 5 -m 60 https://v6r.ipip.net/?format=text"
        ip = execShell(cmd)
        result = ip[0].strip()
        if result == '':
            return '127.0.0.1'
        writeFile(filename, result)
        return result
    finally:
        pass
    return '127.0.0.1'


def inArray(arrays, searchStr):
    # 搜索数据中是否存在
    for key in arrays:
        if key == searchStr:
            return True

    return False

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

def getHostAddr():
    ip_text = getPanelDataDir() + '/iplist.txt'
    if os.path.exists(ip_text):
        return readFile(ip_text).strip()
    return '127.0.0.1'

def checkIp(ip):
    # 检查是否为IPv4地址
    import re
    p = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False

def createLinuxUser(user, group):
    execShell("groupadd {}".format(group))
    execShell('useradd -s /sbin/nologin -g {} {}'.format(user, group))
    return True


def setOwn(filename, user, group=None):
    if isAppleSystem():
        return True

    # 设置用户组
    if not os.path.exists(filename):
        return False
    from pwd import getpwnam
    try:
        user_info = getpwnam(user)
        user = user_info.pw_uid
        if group:
            user_info = getpwnam(group)
        group = user_info.pw_gid
    except:
        if user == 'www':
            createLinuxUser(user)
        # 如果指定用户或组不存在，则使用www
        try:
            user_info = getpwnam('www')
        except:
            createLinuxUser(user)
            user_info = getpwnam('www')
        user = user_info.pw_uid
        group = user_info.pw_gid
    os.chown(filename, user, group)
    return True

def setMode(filename, mode):
    # 设置文件权限
    if not os.path.exists(filename):
        return False
    mode = int(str(mode), 8)
    os.chmod(filename, mode)
    return True

def getSqitePrefix():
    WIN = sys.platform.startswith('win')
    if WIN:  # 如果是 Windows 系统，使用三个斜线
        prefix = 'sqlite:///'
    else:  # 否则使用四个斜线
        prefix = 'sqlite:////'
    return prefix

def checkPort(port):
    # 检查端口是否合法
    ports = ['21', '443', '888']
    if port in ports:
        return False
    intport = int(port)
    if intport < 1 or intport > 65535:
        return False
    return True

def getStrBetween(startStr, endStr, srcStr):
    # 字符串取中间
    start = srcStr.find(startStr)
    if start == -1:
        return None
    end = srcStr.find(endStr)
    if end == -1:
        return None
    return srcStr[start + 1:end]

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

# 获取系统温度
def getSystemDeviceTemperature():
    import psutil
    if not hasattr(psutil, "sensors_temperatures"):
        return False, "platform not supported"
    temps = psutil.sensors_temperatures()
    if not temps:
        return False, "can't read any temperature"
    for name, entries in temps.items():
        for entry in entries:
            return True, entry.label
            # print("%-20s %s °C (high = %s °C, critical = %s °C)" % (
            #     entry.label or name, entry.current, entry.high,
            #     entry.critical))
    return False, ""

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


def getHostPort():
    port_file = getPanelDir() + '/data/port.pl'
    if os.path.exists(port_file):
        return readFile(port_file).strip()
    return '7200'


def setHostPort(port):
    file = getPanelDir() + '/data/port.pl'
    return writeFile(file, port)

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

    debug = M('option').field('name').where('name=?',('debug',)).getField('value')
    if debug == 'open':
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

# 检查端口是否占用
def isOpenPort(port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', int(port)))
        s.shutdown(2)
        return True
    except Exception as e:
        return False

def debugLog(*data):
    if isDebugMode():
        print(data)
    return True


def writeLog(stype, msg, args=()):
    # 写日志
    uid = 0
    # try:
    #     from flask import session
    #     if 'uid' in session:
    #         uid = session['uid']
    # except Exception as e:
    #     print("writeLog:"+str(e))
        # pass
        # writeFileLog(getTracebackInfo())
    return writeDbLog(stype, msg, args, uid)

def writeDbLog(stype, msg, args=(), uid=1):
    try:
        import thisdb
        format_msg = getInfo(msg, args)
        thisdb.addLog(stype, format_msg, uid=uid)
        return True
    except Exception as e:
        print("writeDbLog:"+str(e))
        return False

def writeSpeed(title, used, total, speed=0):
    path = getPanelDir()
    speed_file= path + '/data/panelSpeed.pl'
    # 写进度
    if not title:
        data = {'title': None, 'progress': 0,'total': 0, 'used': 0, 'speed': 0}
    else:
        progress = int((100.0 * used / total))
        data = {'title': title, 'progress': progress,'total': total, 'used': used, 'speed': speed}
    writeFile(speed_file, json.dumps(data))
    return True


def getSpeed():
    path = getPanelDir()
    speed_file= path + '/data/panelSpeed.pl'
    # 取进度
    path = getPanelDir()
    data = readFile(speed_file)
    if not data:
        data = json.dumps({'title': None, 'progress': 0,'total': 0, 'used': 0, 'speed': 0})
        writeFile(speed_file, data)
    return json.loads(data)



def M(table=''):
    import core.db as db
    sql = db.Sql()
    if table == '':
        return sql
    return sql.table(table)


def enDoubleCrypt(key, strings):
    # 加密字符串
    try:
        import base64
        _key = md5(key).encode('utf-8')
        _key = base64.urlsafe_b64encode(_key)

        if type(strings) != bytes:
            strings = strings.encode('utf-8')
        import cryptography
        from cryptography.fernet import Fernet
        f = Fernet(_key)
        result = f.encrypt(strings)
        return result.decode('utf-8')
    except:
        writeFileLog(getTracebackInfo())
        return strings


def deDoubleCrypt(key, strings):
    # 解密字符串
    try:
        import base64
        _key = md5(key).encode('utf-8')
        _key = base64.urlsafe_b64encode(_key)

        if type(strings) != bytes:
            strings = strings.encode('utf-8')
        from cryptography.fernet import Fernet
        f = Fernet(_key)
        result = f.decrypt(strings).decode('utf-8')
        return result
    except:
        writeFileLog(getTracebackInfo())
        return strings

# ------------------------------   network start  -----------------------------

def HttpGet(url, timeout=10):
    """
    发送GET请求
    @url 被请求的URL地址(必需)
    @timeout 超时时间默认60秒
    return string
    """
    if sys.version_info[0] == 2:
        try:
            import urllib2
            import ssl
            if sys.version_info[0] == 2:
                reload(urllib2)
                reload(ssl)
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            response = urllib2.urlopen(url, timeout=timeout)
            return response.read()
        except Exception as ex:
            return str(ex)
    else:
        try:
            import urllib.request
            import ssl
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            response = urllib.request.urlopen(url, timeout=timeout)
            result = response.read()
            if type(result) == bytes:
                result = result.decode('utf-8')
            return result
        except Exception as ex:
            return str(ex)


def HttpGet2(url, timeout):
    import urllib.request

    try:
        import ssl
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
        req = urllib.request.urlopen(url, timeout=timeout)
        result = req.read().decode('utf-8')
        return result

    except Exception as e:
        return str(e)


def httpGet(url, timeout=10):
    return HttpGet2(url, timeout)


def HttpPost(url, data, timeout=10):
    """
    发送POST请求
    @url 被请求的URL地址(必需)
    @data POST参数，可以是字符串或字典(必需)
    @timeout 超时时间默认60秒
    return string
    """
    if sys.version_info[0] == 2:
        try:
            import urllib
            import urllib2
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req, timeout=timeout)
            return response.read()
        except Exception as ex:
            return str(ex)
    else:
        try:
            import urllib.request
            import ssl
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(url, data)
            response = urllib.request.urlopen(req, timeout=timeout)
            result = response.read()
            if type(result) == bytes:
                result = result.decode('utf-8')
            return result
        except Exception as ex:
            return str(ex)


def httpPost(url, data, timeout=10):
    return HttpPost(url, data, timeout)

# ------------------------------   network end  -----------------------------

# ------------------------------   panel start  -----------------------------

def isRestart():
    # 检查是否允许重启
    num = M('tasks').where('status!=?', ('1',)).count()
    if num > 0:
        return False
    return True

def getAcmeDir():
    acme = '/root/.acme.sh'
    if isAppleSystem():
        cmd = "who | sed -n '2, 1p' |awk '{print $1}'"
        user = execShell(cmd)[0].strip()
        acme = '/Users/' + user + '/.acme.sh'
    if not os.path.exists(acme):
        acme = '/.acme.sh'
    return acme


def getAcmeDomainDir(domain):
    acme_dir = getAcmeDir()
    acme_domain = acme_dir + '/' + domain
    acme_domain_ecc = acme_domain + '_ecc'
    if os.path.exists(acme_domain_ecc):
        acme_domain = acme_domain_ecc
    return acme_domain


def fileNameCheck(filename):
    f_strs = [';', '&', '<', '>']
    for fs in f_strs:
        if filename.find(fs) != -1:
            return False
    return True

def triggerTask():
    isTask = getPanelDir() + '/logs/panel_task.lock'
    writeFile(isTask, 'True')

def restartTask():
    initd = getPanelDir() + '/scripts/init.d/mw'
    if os.path.exists(initd):
        cmd = initd + ' ' + 'restart_task'
        os.system(cmd)
    return True

def restartMw():
    restart_file = getPanelDir()+'/data/restart.pl'
    writeFile(restart_file, 'True')
    return True

def panelCmd(method):
    cmd = '/etc/init.d/mw'
    if os.path.exists(cmd):
        execShell(cmd + ' ' + method)
        return

    cmd = mw.getPanelDir() + '/scripts/init.d/mw'
    if os.path.exists(cmd):
        data = execShell(cmd + ' ' + method)
        return

# ------------------------------    panel end    -----------------------------

# ------------------------------ openresty start -----------------------------

def checkWebConfig():
    op_dir = getServerDir() + '/openresty/nginx'
    # "ulimit -n 10240 && " +
    cmd = op_dir + "/sbin/nginx -t -c " + op_dir + "/conf/nginx.conf"
    result = execShell(cmd)
    searchStr = 'test is successful'
    if result[1].find(searchStr) == -1:
        msg = getInfo('配置文件错误: {1}', (result[1],))
        writeLog("软件管理", msg)
        return result[1]
    return True

def restartWeb():
    return opWeb("reload")

def deleteFile(file):
    if os.path.exists(file):
        os.remove(file)

def isInstalledWeb():
    path = getServerDir() + '/openresty/nginx/sbin/nginx'
    if os.path.exists(path):
        return True
    return False

def opWeb(method):
    if not isInstalledWeb():
        return False

    # systemd
    systemd = systemdCfgDir() + '/openresty.service'
    if os.path.exists(systemd):
        execShell('systemctl ' + method + ' openresty')
        return True


    sys_initd = '/etc/init.d/openresty'
    if os.path.exists(sys_initd):
        os.system(sys_initd + ' ' + method)
        return True

    # initd
    initd = getServerDir() + '/openresty/init.d/openresty'
    if os.path.exists(initd):
        execShell(initd + ' ' + method)
        return True

    return False

def opLuaMake(cmd_name):
    path = getServerDir() + '/web_conf/nginx/lua/lua.conf'
    root_dir = getServerDir() + '/web_conf/nginx/lua/' + cmd_name
    dst_path = getServerDir() + '/web_conf/nginx/lua/' + cmd_name + '.lua'
    def_path = getServerDir() + '/web_conf/nginx/lua/empty.lua'

    if not os.path.exists(root_dir):
        execShell('mkdir -p ' + root_dir)

    files = []
    for fl in os.listdir(root_dir):
        suffix = getFileSuffix(fl)
        if suffix != 'lua':
            continue
        flpath = os.path.join(root_dir, fl)
        files.append(flpath)

    if len(files) > 0:
        def_path = dst_path
        content = ''
        for f in files:
            t = readFile(f)
            f_base = os.path.basename(f)
            content += '-- ' + '*' * 20 + ' ' + f_base + ' start ' + '*' * 20 + "\n"
            content += t
            content += "\n" + '-- ' + '*' * 20 + ' ' + f_base + ' end ' + '*' * 20 + "\n"
        writeFile(dst_path, content)
    else:
        if os.path.exists(dst_path):
            os.remove(dst_path)

    conf = readFile(path)
    conf = re.sub(cmd_name + ' (.*);',
                  cmd_name + " " + def_path + ";", conf)
    writeFile(path, conf)


def opLuaInitFile():
    opLuaMake('init_by_lua_file')


def opLuaInitWorkerFile():
    opLuaMake('init_worker_by_lua_file')


def opLuaInitAccessFile():
    opLuaMake('access_by_lua_file')


def opLuaMakeAll():
    opLuaInitFile()
    opLuaInitWorkerFile()
    opLuaInitAccessFile()

# ------------------------------ openresty end -----------------------------

# ---------------------------------------------------------------------------------
# PHP START
# ---------------------------------------------------------------------------------

def getFpmConfFile(version):
    return getServerDir() + '/php/' + version + '/etc/php-fpm.d/www.conf'

def getFpmAddress(version):
    fpm_address = '/tmp/php-cgi-{}.sock'.format(version)
    php_fpm_file = getFpmConfFile(version)
    try:
        content = readFile(php_fpm_file)
        tmp = re.findall(r"listen\s*=\s*(.+)", content)
        if not tmp:
            return fpm_address
        if tmp[0].find('sock') != -1:
            return fpm_address
        if tmp[0].find(':') != -1:
            listen_tmp = tmp[0].split(':')
            if bind:
                fpm_address = (listen_tmp[0], int(listen_tmp[1]))
            else:
                fpm_address = ('127.0.0.1', int(listen_tmp[1]))
        else:
            fpm_address = ('127.0.0.1', int(tmp[0]))
        return fpm_address
    except:
        return fpm_address

def requestFcgiPHP(sock, uri, document_root='/tmp', method='GET', pdata=b''):
    # 直接请求到PHP-FPM
    # version php版本
    # uri 请求uri
    # filename 要执行的php文件
    # args 请求参数
    # method 请求方式

    import utils.php.fpm as fpm
    p = fpm.fpm(sock, document_root)

    if type(pdata) == dict:
        pdata = url_encode(pdata)
    result = p.load_url_public(uri, pdata, method)
    return result
# ---------------------------------------------------------------------------------
# PHP END
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# 数据库 START
# ---------------------------------------------------------------------------------

def getMyORM():
    '''
    获取MySQL资源的ORM
    '''
    import core.orm as orm
    o = orm.ORM()
    return o
# ---------------------------------------------------------------------------------
# 数据库 START
# ---------------------------------------------------------------------------------

##################### notify  start #########################################


def initNotifyConfig():
    p = getNotifyPath()
    if not os.path.exists(p):
        writeFile(p, '{}')
    return True


def getNotifyPath():
    path = 'data/notify.json'
    return path


def getNotifyData(is_parse=False):
    initNotifyConfig()
    notify_file = getNotifyPath()
    notify_data = readFile(notify_file)

    data = json.loads(notify_data)

    if is_parse:
        tag_list = ['tgbot', 'email']
        for t in tag_list:
            if t in data and 'cfg' in data[t]:
                data[t]['data'] = json.loads(deDoubleCrypt(t, data[t]['cfg']))
    return data


def writeNotify(data):
    p = getNotifyPath()
    return writeFile(p, json.dumps(data))


def tgbotNotifyChatID():
    data = getNotifyData(True)
    if 'tgbot' in data and 'enable' in data['tgbot']:
        if data['tgbot']['enable']:
            t = data['tgbot']['data']
            return t['chat_id']
    return ''


def tgbotNotifyObject():
    data = getNotifyData(True)
    if 'tgbot' in data and 'enable' in data['tgbot']:
        if data['tgbot']['enable']:
            t = data['tgbot']['data']
            import telebot
            bot = telebot.TeleBot(app_token)
            return True, bot
    return False, None


def tgbotNotifyMessage(app_token, chat_id, msg):
    import telebot
    bot = telebot.TeleBot(app_token)
    try:
        data = bot.send_message(chat_id, msg)
        return True
    except Exception as e:
        writeFileLog(str(e))
    return False


def tgbotNotifyHttpPost(app_token, chat_id, msg):
    try:
        url = 'https://api.telegram.org/bot' + app_token + '/sendMessage'
        post_data = {
            'chat_id': chat_id,
            'text': msg,
        }
        rdata = httpPost(url, post_data)
        return True
    except Exception as e:
        writeFileLog(str(e))
    return False


def tgbotNotifyTest(app_token, chat_id):
    msg = 'MW-通知验证测试OK'
    return tgbotNotifyHttpPost(app_token, chat_id, msg)


def emailNotifyMessage(data):
    '''
    邮件通知
    '''
    import utils.email as email
    try:
        if data['smtp_ssl'] == 'ssl':
            email.sendSSL(data['smtp_host'], data['smtp_port'],
                           data['username'], data['password'],
                           data['to_mail_addr'], data['subject'], data['content'])
        else:
            email.send(data['smtp_host'], data['smtp_port'],
                        data['username'], data['password'],
                        data['to_mail_addr'], data['subject'], data['content'])
        return True
    except Exception as e:
        print(getTracebackInfo())
    return False


def emailNotifyTest(data):
    # print(data)
    data['subject'] = 'MW通知测试'
    data['content'] = data['mail_test']
    return emailNotifyMessage(data)


def notifyMessageTry(msg, stype='common', trigger_time=300, is_write_log=True):

    lock_file = getPanelTmp() + '/notify_lock.json'
    if not os.path.exists(lock_file):
        writeFile(lock_file, '{}')

    lock_data = json.loads(readFile(lock_file))
    if stype in lock_data:
        diff_time = time.time() - lock_data[stype]['do_time']
        if diff_time >= trigger_time:
            lock_data[stype]['do_time'] = time.time()
        else:
            return False
    else:
        lock_data[stype] = {'do_time': time.time()}

    writeFile(lock_file, json.dumps(lock_data))

    if is_write_log:
        writeLog("通知管理[" + stype + "]", msg)

    data = getNotifyData(True)
    # tag_list = ['tgbot', 'email']
    # tagbot
    do_notify = False
    if 'tgbot' in data and 'enable' in data['tgbot']:
        if data['tgbot']['enable']:
            t = data['tgbot']['data']
            i = sys.version_info

            # telebot 在python小于3.7无法使用
            if i[0] < 3 or i[1] < 7:
                do_notify = tgbotNotifyHttpPost(
                    t['app_token'], t['chat_id'], msg)
            else:
                do_notify = tgbotNotifyMessage(
                    t['app_token'], t['chat_id'], msg)

    if 'email' in data and 'enable' in data['email']:
        if data['email']['enable']:
            t = data['email']['data']
            t['subject'] = 'MW通知'
            t['content'] = msg
            do_notify = emailNotifyMessage(t)
    return do_notify


def notifyMessage(msg, stype='common', trigger_time=300, is_write_log=True):
    try:
        return notifyMessageTry(msg, stype, trigger_time, is_write_log)
    except Exception as e:
        writeFileLog(getTracebackInfo())
        return False


##################### notify  end #########################################

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

