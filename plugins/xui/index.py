# coding:utf-8

import sys
import io
import os
import time
import re

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'xui'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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
    cmd = "ps -ef|grep x-ui |grep -v grep | grep -v python  | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def getServiceFile():
    systemDir = mw.systemdCfgDir()
    return systemDir + '/xui.service'


def getXuiPort():
    return '8349'


def __release_port(port):
    from collections import namedtuple
    try:
        from utils.firewall import Firewall as MwFirewall
        MwFirewall.instance().addAcceptPort(port, 'xui', 'port')
        return port
    except Exception as e:
        return "Release failed {}".format(e)

def __delete_port(port):
    from collections import namedtuple
    try:
        from utils.firewall import Firewall as MwFirewall
        MwFirewall.instance().delAcceptPortCmd(port, 'tcp')
        return port
    except Exception as e:
        return "Delete failed {}".format(e)


def pSqliteDb(dbname='databases'):
    conn = mw.M(dbname).dbPos('/etc/x-ui', 'x-ui')
    return conn

def initDreplace():
    return 'ok'


def xuiOp(method):
    file = initDreplace()

    if not mw.isAppleSystem():
        mw.execShell('systemctl daemon-reload')
        data = mw.execShell('systemctl ' + method + ' x-ui')
        if data[1] == '':
            return 'ok'
        return data[1]

    return 'fail'


def start():
    openPort()
    return xuiOp('start')


def stop():
    closePort()
    return xuiOp('stop')


def restart():
    return xuiOp('restart')


def reload():
    return redisOp('reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status x-ui | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'

def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"
    mw.execShell('systemctl enable x-ui')
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"
    mw.execShell('systemctl disable x-ui')
    return 'ok'

def openPort():
    setting = pSqliteDb('settings')
    port_data = setting.field('id,key,value').where("key=?", ('webPort',)).find()
    port = port_data['value']
    __release_port(port)

def closePort():
    setting = pSqliteDb('settings')
    port_data = setting.field('id,key,value').where("key=?", ('webPort',)).find()
    port = port_data['value']
    __delete_port(port)

def getXuiInfo():

    data = {}
    user = pSqliteDb('users')
    info = user.field('username,password').where("id=?", (1,)).find()

    setting = pSqliteDb('settings')
    port_data = setting.field('id,key,value').where("key=?", ('webPort',)).find()
    path_data = setting.field('id,key,value').where("key=?", ('webBasePath',)).find()

    if path_data is not None:
        data['path'] = path_data['value']
    else:
        data['path'] = '/'

    data['username'] = info['username']
    data['password'] = info['password']
    data['port'] = port_data['value']

    data['ip'] = mw.getHostAddr()
    return mw.returnJson(True, 'ok', data)

def installPreInspection():
    sys = mw.execShell("cat /etc/*-release | grep PRETTY_NAME |awk -F = '{print $2}' | awk -F '\"' '{print $2}'| awk '{print $1}'")

    if sys[1] != '':
        return '不支持该系统'

    sys_id = mw.execShell("cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")

    sysName = sys[0].strip().lower()
    sysId = sys_id[0].strip()

    if sysName in ('opensuse'):
        return '不支持该系统'

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
    elif func == 'install_pre_inspection':
        print(installPreInspection())
    elif func == 'conf':
        print(getServiceFile())
    elif func == 'info':
        print(getXuiInfo())
    else:
        print('error')
