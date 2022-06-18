# coding:utf-8

import sys
import io
import os
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'memcached'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/init.d/memcached"
    return path


def getConfTpl():
    path = getPluginDir() + "/init.d/memcached.tpl"
    return path


def getMemPort():
    path = getConf()
    content = mw.readFile(path)
    rep = 'PORT\s*=\s*(\d*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0]


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
    data = mw.execShell(
        "ps -ef|grep " + getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def initDreplace():

    file_tpl = getConfTpl()
    service_path = mw.getServerDir()

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/memcached'

    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    return file_bin


def memOp(method):
    file = initDreplace()
    data = mw.execShell(file + ' ' + method)
    if data[1] == '':
        return 'ok'
    return data[1]


def start():
    return memOp('start')


def stop():
    return memOp('stop')


def restart():
    return memOp('restart')


def reload():
    return memOp('reload')


def runInfo():
    # 获取memcached状态
    import telnetlib
    import re
    port = getMemPort()
    try:
        tn = telnetlib.Telnet('127.0.0.1', int(port))
        tn.write(b"stats\n")
        tn.write(b"quit\n")
        data = tn.read_all()
        if type(data) == bytes:
            data = data.decode('utf-8')
        data = data.replace('STAT', '').replace('END', '').split("\n")
        result = {}
        res = ['cmd_get', 'get_hits', 'get_misses', 'limit_maxbytes', 'curr_items', 'bytes',
               'evictions', 'limit_maxbytes', 'bytes_written', 'bytes_read', 'curr_connections']
        for d in data:
            if len(d) < 3:
                continue
            t = d.split()
            if not t[0] in res:
                continue
            result[t[0]] = int(t[1])
        result['hit'] = 1
        if result['get_hits'] > 0 and result['cmd_get'] > 0:
            result['hit'] = float(result['get_hits']) / \
                float(result['cmd_get']) * 100

        conf = mw.readFile(getConf())
        result['bind'] = re.search('IP=(.+)', conf).groups()[0]
        result['port'] = int(re.search('PORT=(\d+)', conf).groups()[0])
        result['maxconn'] = int(re.search('MAXCONN=(\d+)', conf).groups()[0])
        result['cachesize'] = int(
            re.search('CACHESIZE=(\d+)', conf).groups()[0])
        return mw.getJson(result)
    except Exception as e:
        return mw.getJson({})


def saveConf():
     # 设置memcached缓存大小
    import re
    confFile = getConf()
    # print confFile
    try:
        args = getArgs()
        content = mw.readFile(confFile)
        content = re.sub('IP=.+', 'IP=' + args['ip'], content)
        content = re.sub('PORT=\d+', 'PORT=' + args['port'], content)
        content = re.sub('MAXCONN=\d+', 'MAXCONN=' + args['maxconn'], content)
        content = re.sub('CACHESIZE=\d+', 'CACHESIZE=' +
                         args['cachesize'], content)
        mw.writeFile(confFile, content)
        restart()
        return 'save ok'
    except Exception as e:
        pass
    return 'fail'


def initdStatus():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mem_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(mem_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)
    mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('chkconfig --del ' + getPluginName())
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'

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
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'conf':
        print(getConf())
    elif func == 'conf_tpl':
        print(getConfTpl())
    elif func == 'save_conf':
        print(saveConf())
    else:
        print('fail')
