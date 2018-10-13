# coding: utf-8

import os
import sys
import time
import string
import json
import hashlib
import shlex
import datetime
import subprocess
import re

from random import Random
from flask import jsonify


def getRunDir():
    return os.getcwd()


def M(table):
    import db
    sql = db.Sql()
    return sql.table(table)


def md5(str):
    # 生成MD5
    try:
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    except:
        return False


def GetFileMd5(filename):
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


def GetRandomString(length):
    # 取随机字符串
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    chrlen = len(chars) - 1
    random = Random()
    for i in range(length):
        str += chars[random.randint(0, chrlen)]
    return str


def checkCode(code, outime=120):
    # 校验验证码
    import web
    try:
        if md5(code.lower()) != web.ctx.session.codeStr:
            web.ctx.session.login_error = getMsg('CODE_ERR')
            return False
        if time.time() - web.ctx.session.codeTime > outime:
            web.ctx.session.login_error = getMsg('CODE_TIMEOUT')
            return False
        return True
    except:
        web.ctx.session.login_error = getMsg('CODE_NOT_EXISTS')
        return False


def retJson(status, msg, data=()):
    return jsonify({'status': status, 'msg': msg, 'data': data})


def returnJson(status, msg, args=()):
    # 取通用Json返回
    return getJson(returnMsg(status, msg, args))


def returnMsg(status, msg, args=()):
    import json
    # 取通用字曲返回
    logMessage = json.loads(
        readFile('static/language/' + get_language() + '/public.json'))
    keys = logMessage.keys()
    if msg in keys:
        msg = logMessage[msg]
        for i in range(len(args)):
            rep = '{' + str(i + 1) + '}'
            msg = msg.replace(rep, args[i])
    return {'status': status, 'msg': msg}


def getMsg(key, args=()):
    # 取提示消息
    try:
        logMessage = json.loads(
            readFile('static/language/' + get_language() + '/public.json'))
        keys = logMessage.keys()
        msg = None
        if key in keys:
            msg = logMessage[key]
            for i in range(len(args)):
                rep = '{' + str(i + 1) + '}'
                msg = msg.replace(rep, args[i])
        return msg
    except:
        return key


def getLan(key):
    # 取提示消息

    logMessage = json.loads(
        readFile('static/language/' + get_language() + '/template.json'))
    keys = logMessage.keys()
    msg = None
    if key in keys:
        msg = logMessage[key]
    return msg


def getJson(data):
    import json
    import web
    web.header('Content-Type', 'application/json; charset=utf-8')
    return json.dumps(data)


def readFile(filename):
    # 读文件内容
    try:
        fp = open(filename, 'r')
        fBody = fp.read()
        fp.close()
        return fBody
    except:
        return False


def getDate():
    # 取格式时间
    import time
    return time.strftime('%Y-%m-%d %X', time.localtime())


def get_language():
    path = 'data/language.pl'
    if not os.path.exists(path):
        return 'Simplified_Chinese'
    return readFile(path).strip()


def WriteLog(type, logMsg, args=()):
    # 写日志
    try:
        import time
        import db
        import json
        logMessage = json.loads(
            readFile('static/language/' + get_language() + '/log.json'))
        keys = logMessage.keys()
        if logMsg in keys:
            logMsg = logMessage[logMsg]
            for i in range(len(args)):
                rep = '{' + str(i + 1) + '}'
                logMsg = logMsg.replace(rep, args[i])
        if type in keys:
            type = logMessage[type]
        sql = db.Sql()
        mDate = time.strftime('%Y-%m-%d %X', time.localtime())
        data = (type, logMsg, mDate)
        result = sql.table('logs').add('type,log,addtime', data)
    except:
        pass


def writeFile(filename, str):
    # 写文件内容
    try:
        fp = open(filename, 'w+')
        fp.write(str)
        fp.close()
        return True
    except:
        return False


def httpGet(url, timeout=30):
    # 发送GET请求
    try:
        import urllib2
        import ssl
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
        response = urllib2.urlopen(url, timeout=timeout)
        return response.read()
    except Exception, ex:
        #WriteLog('网络诊断',str(ex) + '['+url+']');
        return str(ex)


def httpPost(url, data, timeout=30):
    # 发送POST请求
    try:
        import urllib
        import urllib2
        import ssl
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req, timeout=timeout)
        return response.read()
    except Exception, ex:
        #WriteLog('网络诊断',str(ex) + '['+url+']');
        return str(ex)


def writeSpeed(title, used, total, speed=0):
    # 写进度
    if not title:
        data = {'title': None, 'progress': 0,
                'total': 0, 'used': 0, 'speed': 0}
    else:
        progress = int((100.0 * used / total))
        data = {'title': title, 'progress': progress,
                'total': total, 'used': used, 'speed': speed}
    writeFile('/tmp/panelSpeed.pl', json.dumps(data))
    return True


def getSpeed():
    # 取进度
    data = readFile('/tmp/panelSpeed.pl')
    if not data:
        data = json.dumps({'title': None, 'progress': 0,
                           'total': 0, 'used': 0, 'speed': 0})
        writeFile('/tmp/panelSpeed.pl', data)
    return json.loads(data)


def ExecShell(cmdstring, cwd=None, timeout=None, shell=True):

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

    return sub.communicate()


def serviceReload():
    # 重载Web服务配置
    if os.path.exists('/www/server/nginx/sbin/nginx'):
        result = ExecShell('/etc/init.d/nginx reload')
        if result[1].find('nginx.pid') != -1:
            ExecShell('pkill -9 nginx && sleep 1')
            ExecShell('/etc/init.d/nginx start')
    else:
        result = ExecShell('/etc/init.d/httpd reload')
    return result


def phpReload(version):
    # 重载PHP配置
    import os
    if os.path.exists('/www/server/php/' + version + '/libphp5.so'):
        ExecShell('/etc/init.d/httpd reload')
    else:
        ExecShell('/etc/init.d/php-fpm-' + version + ' reload')


def downloadFile(url, filename):
    import urllib
    urllib.urlretrieve(url, filename=filename, reporthook=downloadHook)


def downloadHook(count, blockSize, totalSize):
    speed = {'total': totalSize, 'block': blockSize, 'count': count}
    print speed
    print '%02d%%' % (100.0 * count * blockSize / totalSize)


def GetLocalIp():
    # 取本地外网IP
    try:
        import re
        filename = 'data/iplist.txt'
        ipaddress = readFile(filename)
        if not ipaddress:
            import urllib2
            url = 'http://pv.sohu.com/cityjson?ie=utf-8'
            opener = urllib2.urlopen(url)
            str = opener.read()
            ipaddress = re.search('\d+.\d+.\d+.\d+', str).group(0)
            writeFile(filename, ipaddress)

        ipaddress = re.search('\d+.\d+.\d+.\d+', ipaddress).group(0)
        return ipaddress
    except:
        try:
            url = web.ctx.session.home + '/Api/getIpAddress'
            opener = urllib2.urlopen(url)
            return opener.read()
        except:
            import web
            return web.ctx.host.split(':')[0]

# 搜索数据中是否存在


def inArray(arrays, searchStr):
    for key in arrays:
        if key == searchStr:
            return True

    return False

# 检查Web服务器配置文件是否有错误


def checkWebConfig():
    import web
    if get_webserver() == 'nginx':
        result = ExecShell(
            "ulimit -n 10240 && /www/server/nginx/sbin/nginx -t -c /www/server/nginx/conf/nginx.conf")
        searchStr = 'successful'
    else:
        result = ExecShell(
            "ulimit -n 10240 && /www/server/apache/bin/apachectl -t")
        searchStr = 'Syntax OK'

    if result[1].find(searchStr) == -1:
        WriteLog("TYPE_SOFT", 'CONF_CHECK_ERR', (result[1],))
        return result[1]
    return True

# 检查是否为IPv4地址


def checkIp(ip):
    import re
    p = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False

# 检查端口是否合法


def checkPort(port):
    ports = ['21', '25', '443', '8080', '888', '8888', '8443']
    if port in ports:
        return False
    intport = int(port)
    if intport < 1 or intport > 65535:
        return False
    return True

# 字符串取中间


def getStrBetween(startStr, endStr, srcStr):
    start = srcStr.find(startStr)
    if start == -1:
        return None
    end = srcStr.find(endStr)
    if end == -1:
        return None
    return srcStr[start + 1:end]


def getCpuType():
    # 取CPU类型
    cpuinfo = open('/proc/cpuinfo', 'r').read()
    rep = "model\s+name\s+:\s+(.+)"
    tmp = re.search(rep, cpuinfo)
    cpuType = None
    if tmp:
        cpuType = tmp.groups()[0]
    return cpuType


# 检查是否允许重启
def IsRestart():
    num = M('tasks').where('status!=?', ('1',)).count()
    if num > 0:
        return False
    return True

# 加密密码字符


def hasPwd(password):
    import crypt
    return crypt.crypt(password, password)


# 处理MySQL配置文件
def CheckMyCnf():
    import os
    confFile = '/etc/my.cnf'
    if os.path.exists(confFile):
        conf = readFile(confFile)
        if len(conf) > 100:
            return True
    versionFile = '/www/server/mysql/version.pl'
    if not os.path.exists(versionFile):
        return False

    versions = ['5.1', '5.5', '5.6', '5.7', 'AliSQL']
    version = readFile(versionFile)
    for key in versions:
        if key in version:
            version = key
            break

    shellStr = '''
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

CN='125.88.182.172'
HK='download.bt.cn'
HK2='103.224.251.67'
US='174.139.221.74'
sleep 0.5;
CN_PING=`ping -c 1 -w 1 $CN|grep time=|awk '{print $7}'|sed "s/time=//"`
HK_PING=`ping -c 1 -w 1 $HK|grep time=|awk '{print $7}'|sed "s/time=//"`
HK2_PING=`ping -c 1 -w 1 $HK2|grep time=|awk '{print $7}'|sed "s/time=//"`
US_PING=`ping -c 1 -w 1 $US|grep time=|awk '{print $7}'|sed "s/time=//"`

echo "$HK_PING $HK" > ping.pl
echo "$HK2_PING $HK2" >> ping.pl
echo "$US_PING $US" >> ping.pl
echo "$CN_PING $CN" >> ping.pl
nodeAddr=`sort -V ping.pl|sed -n '1p'|awk '{print $2}'`
if [ "$nodeAddr" == "" ];then
    nodeAddr=$HK
fi

Download_Url=http://$nodeAddr:5880


MySQL_Opt()
{
    MemTotal=`free -m | grep Mem | awk '{print  $2}'`
    if [[ ${MemTotal} -gt 1024 && ${MemTotal} -lt 2048 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 32M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 128#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 768K#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 768K#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 16#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 16M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 32M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 128M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 32M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 2048 && ${MemTotal} -lt 4096 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 64M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 256#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 1M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 1M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 32#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 32M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 64M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 256M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 64M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 4096 && ${MemTotal} -lt 8192 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 128M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 512#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 2M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 2M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 32M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 64#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 64M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 64M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 512M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 128M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 8192 && ${MemTotal} -lt 16384 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 256M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 1024#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 4M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 4M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 64M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 128#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 128M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 128M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 1024M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 256M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 16384 && ${MemTotal} -lt 32768 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 512M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 2048#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 128M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 256#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 256M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 256M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 2048M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 512M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 32768 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 1024M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 4096#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 256M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 512#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 512M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 512M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 4096M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 1024M#" /etc/my.cnf
    fi
}

wget -O /etc/my.cnf $Download_Url/install/conf/mysql-%s.conf -T 5
MySQL_Opt
''' % (version,)
    # 判断是否迁移目录
    if os.path.exists('data/datadir.pl'):
        newPath = public.readFile('data/datadir.pl')
        mycnf = public.readFile('/etc/my.cnf')
        mycnf = mycnf.replace('/www/server/data', newPath)
        public.writeFile('/etc/my.cnf', mycnf)

    os.system(shellStr)
    WriteLog('TYPE_SOFE', 'MYSQL_CHECK_ERR')
    return True


def get_url(timeout=0.5):
    import json
    try:
        nodeFile = '/www/server/panel/data/node.json'
        node_list = json.loads(readFile(nodeFile))
        mnode = None
        for node in node_list:
            node['ping'] = get_timeout(
                node['protocol'] + node['address'] + ':' + node['port'] + '/check.txt')
            if not node['ping']:
                continue
            if not mnode:
                mnode = node
            if node['ping'] < mnode['ping']:
                mnode = node
        return mnode['protocol'] + mnode['address'] + ':' + mnode['port']
    except:
        return 'http://download.bt.cn'


def get_timeout(url):
    start = time.time()
    result = httpGet(url)
    if result != 'True':
        return False
    return int((time.time() - start) * 1000)


# 获取Token
def GetToken():
    try:
        from json import loads
        tokenFile = 'data/token.json'
        if not os.path.exists(tokenFile):
            return False
        token = loads(public.readFile(tokenFile))
        return token
    except:
        return False

# 解密数据


def auth_decode(data):
    token = GetToken()
    # 是否有生成Token
    if not token:
        return returnMsg(False, 'REQUEST_ERR')

    # 校验access_key是否正确
    if token['access_key'] != data['btauth_key']:
        return returnMsg(False, 'REQUEST_ERR')

    # 解码数据
    import binascii
    import hashlib
    import urllib
    import hmac
    import json
    tdata = binascii.unhexlify(data['data'])

    # 校验signature是否正确
    signature = binascii.hexlify(
        hmac.new(token['secret_key'], tdata, digestmod=hashlib.sha256).digest())
    if signature != data['signature']:
        return returnMsg(False, 'REQUEST_ERR')

    # 返回
    return json.loads(urllib.unquote(tdata))


# 数据加密
def auth_encode(data):
    token = GetToken()
    pdata = {}

    # 是否有生成Token
    if not token:
        return returnMsg(False, 'REQUEST_ERR')

    # 生成signature
    import binascii
    import hashlib
    import urllib
    import hmac
    import json
    tdata = urllib.quote(json.dumps(data))
    # 公式  hex(hmac_sha256(data))
    pdata['signature'] = binascii.hexlify(
        hmac.new(token['secret_key'], tdata, digestmod=hashlib.sha256).digest())

    # 加密数据
    pdata['btauth_key'] = token['access_key']
    pdata['data'] = binascii.hexlify(tdata)
    pdata['timestamp'] = time.time()

    # 返回
    return pdata

# 检查Token


def checkToken(get):
    tempFile = 'data/tempToken.json'
    if not os.path.exists(tempFile):
        return False
    import json
    import time
    tempToken = json.loads(readFile(tempFile))
    if time.time() > tempToken['timeout']:
        return False
    if get.token != tempToken['token']:
        return False
    return True

# 获取Web服务器


def get_webserver():
    webserver = 'nginx'
    if not os.path.exists('/www/server/nginx/sbin/nginx'):
        webserver = 'apache'
    return webserver

# 过滤输入


def checkInput(data):
    if not data:
        return data
    if type(data) != str:
        return data
    checkList = [
        {'d': '<', 'r': '＜'},
        {'d': '>', 'r': '＞'},
        {'d': '\'', 'r': '‘'},
        {'d': '"', 'r': '“'},
        {'d': '&', 'r': '＆'},
        {'d': '#', 'r': '＃'},
        {'d': '<', 'r': '＜'}
    ]
    for v in checkList:
        data = data.replace(v['d'], v['r'])
    return data

# 取文件指定尾行数


def GetNumLines(path, num, p=1):
    try:
        import cgi
        if not os.path.exists(path):
            return ""
        start_line = (p - 1) * num
        count = start_line + num
        fp = open(path)
        buf = ""
        fp.seek(-1, 2)
        if fp.read(1) == "\n":
            fp.seek(-1, 2)
        data = []
        b = True
        n = 0
        for i in range(count):
            while True:
                newline_pos = string.rfind(buf, "\n")
                pos = fp.tell()
                if newline_pos != -1:
                    if n >= start_line:
                        line = buf[newline_pos + 1:]
                        try:
                            data.insert(0, cgi.escape(line))
                        except:
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
                    buf = fp.read(to_read) + buf
                    fp.seek(-to_read, 1)
                    if pos - to_read == 0:
                        buf = "\n" + buf
            if not b:
                break
        fp.close()
    except:
        data = []
    return "\n".join(data)

# 验证证书


def CheckCert(certPath='ssl/certificate.pem'):
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
        result = ExecShell(openssl + " x509 -in " +
                           certPath + " -noout -subject")
        if result[1].find('-bash:') != -1:
            return True
        if len(result[1]) > 2:
            return False
        if result[0].find('error:') != -1:
            return False
    return True

 # 获取面板地址


def getPanelAddr():
    import web
    protocol = 'https://' if os.path.exists("data/ssl.pl") else 'http://'
    h = web.ctx.host.split(':')
    try:
        result = protocol + h[0] + ':' + h[1]
    except:
        result = protocol + h[0] + ':' + readFile('data/port.pl').strip()
    return result


# 字节单位转换
def to_size(size):
    d = ('b', 'KB', 'MB', 'GB', 'TB')
    s = d[0]
    for b in d:
        if size < 1024:
            return str(size) + ' ' + b
        size = size / 1024
        s = b
    return str(size) + ' ' + b


def get_string(t):
    if t != -1:
        max = 126
        m_types = [{'m': 122, 'n': 97}, {'m': 90, 'n': 65}, {'m': 57, 'n': 48}, {
            'm': 47, 'n': 32}, {'m': 64, 'n': 58}, {'m': 96, 'n': 91}, {'m': 125, 'n': 123}]
    else:
        max = 256
        t = 0
        m_types = [{'m': 255, 'n': 0}]
    arr = []
    for i in range(max):
        if i < m_types[t]['n'] or i > m_types[t]['m']:
            continue
        arr.append(chr(i))
    return arr


def get_string_find(t):
    if type(t) != list:
        t = [t]
    return_str = ''
    for s1 in t:
        return_str += get_string(int(s1[0]))[int(s1[1:])]
    return return_str


def get_string_arr(t):
    s_arr = {}
    t_arr = []
    for s1 in t:
        for i in range(6):
            if not i in s_arr:
                s_arr[i] = get_string(i)
            for j in range(len(s_arr[i])):
                if s1 == s_arr[i][j]:
                    t_arr.append(str(i) + str(j))
    return t_arr
