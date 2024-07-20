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
    return 'zabbix_agent'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getArgs():
    args = sys.argv[3:]
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

def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'pidfile\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def status():
    cmd = "ps aux|grep zabbix_agentd |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'

def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    return content

def zabbixAgentConf():
    return '/etc/zabbix/zabbix_agentd.conf'

def runLog():
    za_conf = zabbixAgentConf()
    content = mw.readFile(za_conf)

    rep = 'LogFile=\s*(.*)'
    tmp = re.search(rep, content)

    if tmp.groups() == 0:
        return tmp.groups()[0].strip()
    return '/var/log/zabbix/zabbix_agentd.log'

def initAgentConf():
    za_src_tpl = getPluginDir()+'/conf/zabbix_agentd.conf'
    za_dst_path = zabbixAgentConf()

    # zabbix_agent配置
    content = mw.readFile(za_src_tpl)
    content = contentReplace(content)
    mw.writeFile(za_dst_path, content)

def initDreplace():
    init_file = getServerDir() + '/init.pl'
    if not os.path.exists(init_file):
        initAgentConf()
        openPort()
        mw.writeFile(init_file, 'ok')
    return True

def openPort():
    try:
        import firewall_api
        firewall_api.firewall_api().addAcceptPortArgs('10050', 'zabbix-agent', 'port')
        return port
    except Exception as e:
        return "Release failed {}".format(e)
    return True

def zOp(method):

    initDreplace()

    data = mw.execShell('systemctl ' + method + ' zabbix-agent')
    if data[1] == '':
        return 'ok'
    return data[1]


def start():
    
    return zOp('start')


def stop():
    val = zOp('stop')
    return val

def restart():
    status = zOp('restart')
    return status

def reload():
    return zOp('reload')

def initdStatus():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status zabbix-agent | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    mw.execShell('systemctl enable zabbix-agent')
    return 'ok'


def initdUinstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    mw.execShell('systemctl disable zabbix-agent')
    return 'ok'


def installPreInspection():
    zabbix_dir = mw.getServerDir()+'/zabbix'
    if os.path.exists(zabbix_dir):
        return '已经安装zabbix插件'
    return 'ok'


def uninstallPreInspection():
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
    elif func == 'uninstall_pre_inspection':
        print(uninstallPreInspection())
    elif func == 'conf':
        print(zabbixAgentConf())
    elif func == 'zabbix_agent_conf':
        print(zabbixAgentConf())
    elif func == 'run_log':
        print(runLog())
    else:
        print('error')
