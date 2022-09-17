# coding:utf-8

import sys
import io
import os
import time

from datetime import datetime

try:
    import dns.resolver
except:
    if os.path.exists(os.getcwd() + '/bin'):
        mw.mw(os.getcwd() + '/bin/pip install dnspython')
    else:
        mw.execShell('pip install dnspython')
    import dns.resolver


sys.path.append(os.getcwd() + "/class/core")

import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'mail'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[3:]
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
    return 'start'


def M(dbname='domain'):
    file = getServerDir() + '/postfixadmin.db'
    name = 'mail'
    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        csql = mw.readFile(getPluginDir() + '/conf/postfixadmin.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())
    else:
        # 现有run
        # conn = mw.M(dbname).dbPos(getServerDir(), name)
        # csql = mw.readFile(getPluginDir() + '/conf/mysql.sql')
        # csql_list = csql.split(';')
        # for index in range(len(csql_list)):
        #     conn.execute(csql_list[index], ())
        conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn


def __check_a(hostname):
    key = '{0}:{1}'.format(hostname, 'A')
    now = int(time.time())

    value = ""
    error_ip = ""

    ipaddress = mw.getLocalIp()
    if not ipaddress:
        return False, {"status": 0, "v_time": now, "value": error_ip}

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 1
        try:
            result = resolver.resolve(hostname, 'A')
        except:
            result = resolver.query(hostname, 'A')

        for i in result.response.answer:
            for j in i.items:
                error_ip = j
                if str(j).strip() in ipaddress:
                    value = str(j).strip()

        if value:
            return True, {"status": 1, "v_time": now, "value": value}
        return False, {"status": 0, "v_time": now, "value": error_ip}
    except Exception as e:
        raise e
    return False, {"status": 0, "v_time": now, "value": error_ip}


def addDomain():
    args = getArgs()

    if 'domain' not in args:
        return mw.returnJson(False, '请传入域名')

    domain = args['domain']
    a_record = args['a_record']

    if not a_record.endswith(domain):
        return mw.returnJson(False, 'A记录 [{}] 不属于该域名'.format(a_record))

    if not mw.isDebugMode():
        check = __check_a(a_record)
        if not check[0]:
            return mw.returnJson(False, 'A记录解析失败<br>域名：{}<br>IP：{}'.format(a_record, check[1]['value']))

    if M('domain').where("domain=?", (domain,)).count() > 0:
        return mw.returnJson(False, '该域名已存在')

    cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        M('domain').add('domain,a_record,created',
                        (domain, a_record, cur_time))
    except:
        return mw.returnJson(False, '邮局没有初始化成功！<br>'
                             '请尝试重新初始化,<br>'
                             '如果以下端口没访问将无法初始化 <br>port 25 [outbound direction]<br> '
                             '你可以尝试执行以下命令测试端口是否开启:<br><br> [ telnet gmail-smtp-in.l.google.com 25 ] <br> ')

    # 在虚拟用户家目录创建对应域名的目录
    if os.path.exists('/www/vmail'):
        if not os.path.exists('/www/vmail/{0}'.format(domain)):
            os.makedirs('/www/vmail/{0}'.format(domain))
        mw.execShell('chown -R vmail:mail /www/vmail/{0}'.format(domain))
    return mw.returnJson(False, 'OK')


def runLog():
    path = '/var/log/maillog'
    # if "ubuntu" in:
    #     path = '/var/log/mail.log'
    return path

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    elif func == 'add_domain':
        print(addDomain())
    else:
        print('error')
