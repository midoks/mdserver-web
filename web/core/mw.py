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

    success = data[0]
    error = data[1]
    # python3 fix 返回byte数据
    if isinstance(success, bytes):
        # success = str(success, encoding='utf-8')
        try:
            success = success.decode('utf-8')
        except Exception as e:
            success = str(e)

    if isinstance(error, bytes):
        # error = str(error, encoding='utf-8')
        try:
            error = error.decode('utf-8')
        except Exception as e:
            error = str(e)
    return (success, error)


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

def getPanelLogs():
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

def getPanelTaskExecLog():
    return getMWLogs() + '/panel_exec.log'

def getWwwDir():
    import thisdb
    site_path = thisdb.getOption('site_path', default=getFatherDir()+'/wwwroot')
    return site_path

def getBackupDir():
    import thisdb
    backup_path = thisdb.getOption('backup_path', default=getFatherDir()+'/backup')
    return backup_path

def setBackupDir(bdir):
    import thisdb
    thisdb.setOption('backup_path', bdir)
    return True

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

def checkCert(certPath='ssl/certificate.pem'):
    # 验证证书
    openssl = '/usr/bin/openssl'
    if not os.path.exists(openssl):
        openssl = '/usr/local/openssl/bin/openssl'
    if not os.path.exists(openssl):
        openssl = 'openssl'
    certPem = readFile(certPath)
    s = "\n-----BEGIN CERTIFICATE-----"
    tmp = certPem.strip().split(s)
    for tmp1 in tmp:
        if tmp1.find('-----BEGIN CERTIFICATE-----') == -1:
            tmp1 = s + tmp1
        writeFile(certPath, tmp1)
        result = execShell(openssl + " x509 -in " +
                           certPath + " -noout -subject")
        if result[1].find('-bash:') != -1:
            return True
        if len(result[1]) > 2:
            return False
        if result[0].find('error:') != -1:
            return False
    return True

def sortFileList(path, ftype = 'mtime', sort = 'desc'):
    flist = os.listdir(path)
    if ftype == 'mtime':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(os.path.join(path,f)), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(os.path.join(path,f)), reverse=False)

    if ftype == 'size':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getsize(os.path.join(path,f)), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getsize(os.path.join(path,f)), reverse=False)

    if ftype == 'fname':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.join(path,f), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.join(path,f), reverse=False)
    return flist


def sortAllFileList(path, ftype = 'mtime', sort = 'desc', search = '',limit = 3000):
    count = 0
    flist = []
    for d_list in os.walk(path):
        if count >= limit:
            break

        for d in d_list[1]:
            if count >= limit:
                break
            if d.lower().find(search) != -1:
                filename = d_list[0] + '/' + d
                if not os.path.exists(filename):
                    continue
                count += 1
                flist.append(filename)

        for f in d_list[2]:
            if count >= limit:
                break

            if f.lower().find(search) != -1:
                filename = d_list[0] + '/' + f
                if not os.path.exists(filename):
                    continue
                count += 1
                flist.append(filename)

    if ftype == 'mtime':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(f), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(f), reverse=False)

    if ftype == 'size':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getsize(f), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getsize(f), reverse=False)
    return flist

def getPathSize(path):
    # 取文件或目录大小
    if not os.path.exists(path):
        return 0
    if not os.path.isdir(path):
        return os.path.getsize(path)
    size_total = 0
    for nf in os.walk(path):
        for f in nf[2]:
            filename = nf[0] + '/' + f
            size_total += os.path.getsize(filename)
    return size_total

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
    if data is None:
        return {'status': status, 'msg': msg}
    return {'status': status, 'msg': msg, 'data': data}

def returnJson(status, msg, data=None):
    if data is None:
        return getJson({'status': status, 'msg': msg})
    return getJson({'status': status, 'msg': msg, 'data': data})

def readFile(filename):
    # 读文件内容
    try:
        fp = open(filename, 'r')
        fBody = fp.read()
        fp.close()
        return fBody
    except Exception as e:
        # print('readFile:',str(e))
        return False

def writeFile(filename, content, mode='w+'):
    # 写文件内容
    try:
        fp = open(filename, mode)
        fp.write(content)
        fp.close()
        return True
    except Exception as e:
        writeFileLog(getTracebackInfo())
        return False


def backFile(file, act=None):
    """
        @name 备份配置文件
        @param file 需要备份的文件
        @param act 如果存在，则备份一份作为默认配置
    """
    file_type = "_bak"
    if act:
        file_type = "_def"

    # print("cp -p {0} {1}".format(file, file + file_type))
    execShell("cp -p {0} {1}".format(file, file + file_type))


def removeBackFile(file, act=None):
    """
        @name 删除备份配置文件
        @param file 需要删除备份文件
        @param act 如果存在，则还原默认配置
    """
    file_type = "_bak"
    if act:
        file_type = "_def"
    execShell("rm -rf {0}".format(file + file_type))


def restoreFile(file, act=None):
    """
        @name 还原配置文件
        @param file 需要还原的文件
        @param act 如果存在，则还原默认配置
    """
    file_type = "_bak"
    if act:
        file_type = "_def"
    execShell("cp -p {1} {0}".format(file, file + file_type))

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

def hasPwd(password):
    # 加密密码字符
    import crypt
    return crypt.crypt(password, password)
    
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


def getHost(port=False):
    from flask import request
    host_tmp = request.headers.get('host')
    if not host_tmp:
        if request.url_root:
            tmp = re.findall(r"(https|http)://([\w:\.-]+)", request.url_root)
            if tmp:
                host_tmp = tmp[0][1]
    if not host_tmp:
        host_tmp = getLocalIp() + ':' + readFile('data/port.pl').strip()
    try:
        if host_tmp.find(':') == -1:
            host_tmp += ':80'
    except:
        host_tmp = "127.0.0.1:8888"
    h = host_tmp.split(':')
    if port:
        return h[-1]
    return ':'.join(h[0:-1])

def getClientIp():
    from flask import request
    return request.remote_addr.replace('::ffff:', '')

def checkDomainPanel():
    import thisdb
    from flask import Flask, redirect, request, url_for
    
    current_host = getHost()
    domain = thisdb.getOption('panel_domain', default='')
    port = getPanelPort()
    scheme = 'http'

    panel_ssl_data = thisdb.getOptionByJson('panel_ssl', default={'open':False})
    if panel_ssl_data['open']:
        if not inArray(['local','nginx'], panel_ssl_data['choose']):
            return False
        scheme = 'https'

    client_ip = getClientIp()
    if client_ip in ['127.0.0.1', 'localhost', '::1']:
        return False

    ip = getHostAddr()
    if domain == '':
        if ip in ['127.0.0.1', 'localhost', '::1']:
            return False
        if current_host.strip().lower() != ip.strip().lower():
            to = scheme + "://" + ip + ":" + str(port)
            return redirect(to, code=302)
        return False
    else:
        # print(current_host.strip().lower(), domain.strip().lower())
        if current_host.strip().lower() != domain.strip().lower():
            to = scheme + "://" + domain + ":" + str(port)
            return redirect(to, code=302)
    return False

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
def getFileStatsDesc(filename, path=None):
    import pwd
    if path == '' or filename == '':
        return ';;;;;'
    try:
        filename = filename.replace('//', '/')
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


def getLanguage():
    panel_dir = getPanelDir()
    path = panel_dir+'/data/language.pl'
    if not os.path.exists(path):
        return 'Simplified_Chinese'
    return readFile(path).strip()


def getStaticJson(name="public"):
    file = 'static/language/' + getLanguage() + '/' + name + '.json'
    if not os.path.exists(file):
        file = 'route/static/language/' + getLanguage() + '/' + name + '.json'
    return file


def returnMsg(status, msg, args=()):
    # 取通用字曲返回
    pjson = getStaticJson('public')
    logMessage = json.loads(readFile(pjson))
    keys = logMessage.keys()

    if msg in keys:
        msg = logMessage[msg]
        for i in range(len(args)):
            rep = '{' + str(i + 1) + '}'
            msg = msg.replace(rep, args[i])
    return {'status': status, 'msg': msg, 'data': args}
    
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

def writeFileLog(msg, path=None, limit_size=50 * 1024 * 1024, save_limit=3):
    log_file = getPanelDir() + '/logs/debug.log'
    if path != None:
        log_file = path

    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
        if size > limit_size:
            log_file_rename = log_file + "_" + \
                time.strftime("%Y-%m-%d_%H%M%S") + '.log'
            os.rename(log_file, log_file_rename)
            logs = sorted(glob.glob(log_file + "_*"))
            count = len(logs)
            save_limit = count - save_limit
            for i in range(count):
                if i > save_limit:
                    break
                os.remove(logs[i])
                # print('|---多余日志[' + logs[i] + ']已删除!')

    f = open(log_file, 'ab+')
    msg += "\n"
    if __name__ == '__main__':
        print(msg)
    f.write(msg.encode('utf-8'))
    f.close()
    return True

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
    panel_dir = getPanelDir()
    speed_file= panel_dir + '/data/panel_speed.pl'
    # 写进度
    if not title:
        data = {'title': None, 'progress': 0,'total': 0, 'used': 0, 'speed': 0}
    else:
        progress = int((100.0 * used / total))
        data = {'title': title, 'progress': progress,'total': total, 'used': used, 'speed': speed}
    writeFile(speed_file, json.dumps(data))
    return True


def getSpeed():
    panel_dir = getPanelDir()
    speed_file= panel_dir + '/data/panel_speed.pl'
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

def aesEncrypt(data, key='ABCDEFGHIJKLMNOP', vi='0102030405060708'):
    # aes加密
    # @param data 被加密的数据
    # @param key 加解密密匙 16位
    # @param vi 16位

    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    if not isinstance(data, bytes):
        data = data.encode()

    # AES_CBC_KEY = os.urandom(32)
    # AES_CBC_IV = os.urandom(16)

    AES_CBC_KEY = key.encode()
    AES_CBC_IV = vi.encode()

    # print("AES_CBC_KEY:", AES_CBC_KEY)
    # print("AES_CBC_IV:", AES_CBC_IV)

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(AES_CBC_KEY),
                    modes.CBC(AES_CBC_IV),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    edata = encryptor.update(padded_data)

    # print(edata)
    # print(str(edata))
    # print(edata.decode())
    return edata


def aesDecrypt(data, key='ABCDEFGHIJKLMNOP', vi='0102030405060708'):
    # aes加密
    # @param data 被解密的数据
    # @param key 加解密密匙 16位
    # @param vi 16位

    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    if not isinstance(data, bytes):
        data = data.encode()

    AES_CBC_KEY = key.encode()
    AES_CBC_IV = vi.encode()

    cipher = Cipher(algorithms.AES(AES_CBC_KEY),
                    modes.CBC(AES_CBC_IV),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    ddata = decryptor.update(data)

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(ddata)

    try:
        uppadded_data = data + unpadder.finalize()
    except ValueError:
        raise Exception('无效的加密信息!')

    return uppadded_data

def aesEncrypt_Crypto(data, key, vi):
    # 该方法保留，暂时不使用
    # aes加密
    # @param data 被加密的数据
    # @param key 加解密密匙 16位
    # @param vi 16位

    from Crypto.Cipher import AES
    cryptor = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
    # 判断是否含有中文
    zhmodel = re.compile(u'[\u4e00-\u9fff]')
    match = zhmodel.search(data)
    if match == None:
        # 无中文时
        add = 16 - len(data) % 16
        pad = lambda s: s + add * chr(add)
        data = pad(data)
        enctext = cryptor.encrypt(data.encode('utf8'))
    else:
        # 含有中文时
        data = data.encode()
        add = 16 - len(data) % 16
        data = data + add * (chr(add)).encode()
        enctext = cryptor.encrypt(data)
    encodestrs = base64.b64encode(enctext).decode('utf8')
    return encodestrs


def aesDecrypt_Crypto(data, key, vi):
    # 该方法保留，暂时不使用
    # aes加密
    # @param data 被加密的数据
    # @param key 加解密密匙 16位
    # @param vi 16位

    from crypto.Cipher import AES
    data = data.encode('utf8')
    encodebytes = base64.urlsafe_b64decode(data)
    cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
    text_decrypted = cipher.decrypt(encodebytes)
    # 判断是否含有中文
    zhmodel = re.compile(u'[\u4e00-\u9fff]')
    match = zhmodel.search(text_decrypted)
    if match == False:
        # 无中文时补位
        unpad = lambda s: s[0:-s[-1]]
        text_decrypted = unpad(text_decrypted)
    text_decrypted = text_decrypted.decode('utf8').rstrip()  # 去掉补位的右侧空格
    return text_decrypted

def getDefault(data,val,def_val=''):
    if val in data:
        return data[val]
    return def_val

def encodeImage(imgsrc, newsrc):
    # 图片加密
    import struct
    old_fp = open(imgsrc, 'rb')
    imgFile = old_fp.read()
    old_fp.close()

    new_fp = open(newsrc,"wb")
    for x in imgFile:
        value = x ^ 86
        value = hex(value)
        s = struct.pack('B',int(value,16))
        new_fp.write(s)
    new_fp.close()
    return True
    
def buildSoftLink(src, dst, force=False):
    '''
    建立软连接
    '''
    if not os.path.exists(src):
        return False

    if os.path.exists(dst) and force:
        os.remove(dst)

    if not os.path.exists(dst):
        execShell('ln -sf "' + src + '" "' + dst + '"')
        return True
    return False
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

def getTriggerTaskLockFile():
    return getPanelDir() + '/logs/panel_task.lock'

def triggerTask():
    lock_file = getTriggerTaskLockFile()
    writeFile(lock_file, 'True')

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

    cmd = getPanelDir() + '/scripts/init.d/mw'
    if os.path.exists(cmd):
        data = execShell(cmd + ' ' + method)
        return

# ------------------------------    panel end    -----------------------------

# ------------------------------ openresty start -----------------------------

def getOpVer():
    version = ''
    version_file_pl = getServerDir() + '/openresty/version.pl'
    if os.path.exists(version_file_pl):
        version = readFile(version_file_pl)
        version = version.strip()
    return version

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

def isIpAddr(ip):
    check_ip = re.compile(r'^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\\d)$')
    if check_ip.match(ip):
        return True
    else:
        return False

def isVaildIpV4(ip):
    import ipaddress
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

def isVaildIpV6(ip):
    import ipaddress
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

def isVaildIp(ip):
    import ipaddress
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        pass

    try:
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        pass
    return False


def getWebStatus():
    pid = getServerDir() + '/openresty/nginx/logs/nginx.pid'
    if os.path.exists(pid):
        return True
    return False


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

##################### ssl start #########################################

def strfDate(sdate):
    return time.strftime('%Y-%m-%d', time.strptime(sdate, '%Y%m%d%H%M%S'))

# 获取证书名称
def getCertName(certPath):
    if not os.path.exists(certPath):
        return None
    try:
        import OpenSSL
        result = {}
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, readFile(certPath))
        # 取产品名称
        issuer = x509.get_issuer()
        result['issuer'] = ''
        if hasattr(issuer, 'CN'):
            result['issuer'] = issuer.CN
        if not result['issuer']:
            is_key = [b'0', '0']
            issue_comp = issuer.get_components()
            if len(issue_comp) == 1:
                is_key = [b'CN', 'CN']
            for iss in issue_comp:
                if iss[0] in is_key:
                    result['issuer'] = iss[1].decode()
                    break
        if not result['issuer']:
            if hasattr(issuer, 'O'):
                result['issuer'] = issuer.O
        # 取到期时间
        result['notAfter'] = strfDate(bytes.decode(x509.get_notAfter())[:-1])
        # 取申请时间
        result['notBefore'] = strfDate(bytes.decode(x509.get_notBefore())[:-1])
        # 取可选名称
        result['dns'] = []
        for i in range(x509.get_extension_count()):
            s_name = x509.get_extension(i)
            if s_name.get_short_name() in [b'subjectAltName', 'subjectAltName']:
                s_dns = str(s_name).split(',')
                for d in s_dns:
                    result['dns'].append(d.split(':')[1])
        subject = x509.get_subject().get_components()
        # 取主要认证名称
        if len(subject) == 1:
            result['subject'] = subject[0][1].decode()
        else:
            if not result['dns']:
                for sub in subject:
                    if sub[0] == b'CN':
                        result['subject'] = sub[1].decode()
                        break
                if 'subject' in result:
                    result['dns'].append(result['subject'])
            else:
                result['subject'] = result['dns'][0]
        result['endtime'] = int(int(time.mktime(time.strptime(
            result['notAfter'], "%Y-%m-%d")) - time.time()) / 86400)
        return result
    except Exception as e:
        writeFileLog(getTracebackInfo())
        return None

def createLocalSSL():
    pdir = getPanelDir()
    local_dir = pdir+'/ssl/local'
    if not os.path.exists(local_dir):
        execShell('mkdir -p ' + local_dir)

    # 自签证书
    # if os.path.exists('ssl/local/input.pl'):
    #     return True

    client_ip = getClientIp()

    import OpenSSL
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
    cert = OpenSSL.crypto.X509()
    cert.set_serial_number(0)
    
    if client_ip == '127.0.0.1':
        cert.get_subject().CN = '127.0.0.1'
    else:
        cert.get_subject().CN = getLocalIp()
    
    cert.set_issuer(cert.get_subject())
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(86400 * 3650)
    cert.set_pubkey(key)
    cert.sign(key, 'md5')
    cert_ca = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    private_key = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
    if len(cert_ca) > 100 and len(private_key) > 100:
        writeFile(local_dir+'/cert.pem', cert_ca, 'wb+')
        writeFile(local_dir+'/private.pem', private_key, 'wb+')
        return True
    return False


def getSSHPort():
    try:
        file = '/etc/ssh/sshd_config'
        conf = readFile(file)
        rep = "(#*)?Port\\s+([0-9]+)\\s*\n"
        port = re.search(rep, conf).groups(0)[1]
        return int(port)
    except:
        return 22


def getSSHStatus():
    if os.path.exists('/usr/bin/apt-get'):
        status = execShell("service ssh status | grep -P '(dead|stop)'")
    else:
        import system_api
        version = system_api.system_api().getSystemVersion()
        if version.find(' Mac ') != -1:
            return True
        if version.find(' 7.') != -1:
            status = execShell("systemctl status sshd.service | grep 'dead'")
        else:
            status = execShell(
                "/etc/init.d/sshd status | grep -e 'stopped' -e '已停'")
    if len(status[0]) > 3:
        status = False
    else:
        status = True
    return status

##################### ssl  end #########################################

def getGlibcVersion():
    try:
        cmd_result = execShell("ldd --version")[0]
        if not cmd_result: return ''
        glibc_version = cmd_result.split("\n")[0].split()[-1]
    except:
        return ''
    return glibc_version

##################### ssh  start #########################################
def getSshDir():
    if isAppleSystem():
        user = execShell("who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return '/Users/' + user + '/.ssh'
    return '/root/.ssh'


def processExists(pname, exe=None, cmdline=None):
    # 进程是否存在
    try:
        import psutil
        pids = psutil.pids()
        for pid in pids:
            try:
                p = psutil.Process(pid)
                if p.name() == pname:
                    if not exe and not cmdline:
                        return True
                    else:
                        if exe:
                            if p.exe() == exe:
                                return True
                        if cmdline:
                            if cmdline in p.cmdline():
                                return True
            except:
                pass
        return False
    except:
        return True


def createRsa():
    # ssh-keygen -t rsa -P "" -C "midoks@163.com"
    ssh_dir = getSshDir()
    # mw.execShell("rm -f /root/.ssh/*")
    if not os.path.exists(ssh_dir + '/authorized_keys'):
        execShell('touch ' + ssh_dir + '/authorized_keys')

    if not os.path.exists(ssh_dir + '/id_rsa.pub') and os.path.exists(ssh_dir + '/id_rsa'):
        execShell('echo y | ssh-keygen -q -t rsa -P "" -f ' +
                  ssh_dir + '/id_rsa')
    else:
        execShell('ssh-keygen -q -t rsa -P "" -f ' + ssh_dir + '/id_rsa')

    execShell('cat ' + ssh_dir + '/id_rsa.pub >> ' +
              ssh_dir + '/authorized_keys')
    execShell('chmod 600 ' + ssh_dir + '/authorized_keys')


def createSshInfo():
    ssh_dir = getSshDir()
    if not os.path.exists(ssh_dir + '/id_rsa') or not os.path.exists(ssh_dir + '/id_rsa.pub'):
        createRsa()

    # 检查是否写入authorized_keys
    data = execShell("cat " + ssh_dir + "/id_rsa.pub | awk '{print $3}'")
    if data[0] != "":
        cmd = "cat " + ssh_dir + "/authorized_keys | grep " + data[0]
        ak_data = execShell(cmd)
        if ak_data[0] == "":
            cmd = 'cat ' + ssh_dir + '/id_rsa.pub >> ' + ssh_dir + '/authorized_keys'
            execShell(cmd)
            execShell('chmod 600 ' + ssh_dir + '/authorized_keys')


def connectSsh():
    import paramiko
    ssh = paramiko.SSHClient()
    createSshInfo()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    port = getSSHPort()
    try:
        ssh.connect('127.0.0.1', port, timeout=5)
    except Exception as e:
        ssh.connect('localhost', port, timeout=5)
    except Exception as e:
        ssh.connect(getHostAddr(), port, timeout=30)
    except Exception as e:
        return False

    shell = ssh.invoke_shell(term='xterm', width=83, height=21)
    shell.setblocking(0)
    return shell


def clearSsh():
    # 服务器IP
    ip = getHostAddr()
    sh = '''
#!/bin/bash
PLIST=`who | grep localhost | awk '{print $2}'`
for i in $PLIST
do
    ps -t /dev/$i |grep -v TTY | awk '{print $1}' | xargs kill -9
done

# getHostAddr
PLIST=`who | grep "${ip}" | awk '{print $2}'`
for i in $PLIST
do
    ps -t /dev/$i |grep -v TTY | awk '{print $1}' | xargs kill -9
done
'''
    if not isAppleSystem():
        info = execShell(sh)
        print(info[0], info[1])
##################### ssh  end   #########################################
        
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
        return str(e)
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
            r = email.sendSSL(data['smtp_host'], data['smtp_port'],
                           data['username'], data['password'],
                           data['to_mail_addr'], data['subject'], data['content'])
        else:
            r = email.send(data['smtp_host'], data['smtp_port'],
                        data['username'], data['password'],
                        data['to_mail_addr'], data['subject'], data['content'])

            print(r)
        return True
    except Exception as e:
        print(getTracebackInfo())
        return str(e)
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

