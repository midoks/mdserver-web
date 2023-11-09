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


import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)


def getPluginName():
    return 'memcached'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()

    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/init.d/memcached"
    return path


def getConfEnv():
    path = getServerDir() + "/memcached.env"
    return path


def getConfTpl():
    path = getPluginDir() + "/init.d/memcached.tpl"
    return path


def getMemPort():
    path = getServerDir() + '/memcached.env'
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
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':')
            tmp[t[0]] = t[1]
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]
    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():
    cmd = "ps aux|grep " + getPluginName() + " |grep -v grep | grep -v mdserver-web | awk '{print $2}'"
    # print(cmd)
    data = mw.execShell(cmd)
    # print(data)
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

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/memcached.service'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/memcached.service.tpl'
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    envFile = getServerDir() + '/memcached.env'
    if not os.path.exists(envFile):
        wbody = "IP=127.0.0.1\n"
        wbody = wbody + "PORT=11211\n"
        wbody = wbody + "USER=root\n"
        wbody = wbody + "MAXCONN=1024\n"
        wbody = wbody + "CACHESIZE=1024\n"
        wbody = wbody + "OPTIONS=''\n"
        mw.writeFile(envFile, wbody)

    return file_bin


def memOp(method):
    file = initDreplace()

    current_os = mw.getOs()
    if current_os == "darwin":
        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    if current_os.startswith("freebsd"):
        data = mw.execShell('service ' + getPluginName() + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
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

        conf = mw.readFile(getServerDir() + '/memcached.env')
        result['bind'] = re.search('IP=(.+)', conf).groups()[0]
        result['port'] = int(re.search('PORT=(\d+)', conf).groups()[0])
        result['maxconn'] = int(re.search('MAXCONN=(\d+)', conf).groups()[0])
        result['cachesize'] = int(
            re.search('CACHESIZE=(\d+)', conf).groups()[0])
        return mw.getJson(result)
    except Exception as e:
        return mw.getJson({})


def saveConf():

    args = getArgs()
    data = checkArgs(args, ['ip', 'port', 'maxconn', 'maxsize'])
    if not data[0]:
        return data[1]

    envFile = getServerDir() + '/memcached.env'

    wbody = "IP=" + args['ip'] + "\n"
    wbody = wbody + "PORT=" + args['port'] + "\n"
    wbody = wbody + "USER=root\n"
    wbody = wbody + "MAXCONN=" + args['maxconn'] + "\n"
    wbody = wbody + "CACHESIZE=" + args['maxconn'] + "\n"
    wbody = wbody + "OPTIONS=''\n"
    mw.writeFile(envFile, wbody)

    restart()
    return 'save ok'


def initdStatus():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        if os.path.exists(initd_bin):
            return 'ok'

    shell_cmd = 'systemctl status ' + \
        getPluginName() + ' | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    # freebsd initd install
    if current_os.startswith('freebsd'):
        import shutil
        source_bin = initDreplace()
        initd_bin = getInitDFile()
        shutil.copyfile(source_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)
        mw.execShell('sysrc ' + getPluginName() + '_enable="YES"')
        return 'ok'

    mw.execShell('systemctl enable ' + getPluginName())
    return 'ok'


def initdUinstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        os.remove(initd_bin)
        mw.execShell('sysrc ' + getPluginName() + '_enable="NO"')
        return 'ok'

    mw.execShell('systemctl disable ' + getPluginName())
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
    elif func == 'conf_env':
        print(getConfEnv())
    elif func == 'save_conf':
        print(saveConf())
    else:
        print('error')
