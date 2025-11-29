# coding: utf-8


import time
import os
import sys
import re
import subprocess

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'doh'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':', 1)
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':', 1)
            tmp[t[0]] = t[1]

    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def getInitdConfTpl():
    path = getPluginDir() + "/init.d/gitea.tpl"
    return path


def getInitdConf():
    path = getServerDir() + "/init.d/doh"
    return path

    if not os.path.exists(path):
        return mw.returnJson(False, "请先安装初始化!<br/>默认地址:http://" + mw.getLocalIp() + ":3000")
    return path


def getConfTpl():
    path = getPluginDir() + "/config/config.toml"
    return path


def status():
    data = mw.execShell(
        "ps -ef|grep " + getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def getHomeDir():
    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return '/Users/' + user
    else:
        return 'www'



def contentReplace(content):

    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    return content


def initDreplace():

    file_tpl = getInitdConfTpl()
    service_path = mw.getServerDir()


    conf_toml = getServerDir() + '/config.toml'
    if not os.path.exists(conf_toml):
        conf_tpl = getConfTpl()
        content = mw.readFile(conf_tpl)
        mw.writeFile(conf_toml, content)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/doh.service'
    systemServiceTpl = getPluginDir() + '/init.d/doh.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    log_path = getServerDir() + '/log'
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    return ''




def appOp(method):
    initDreplace()
    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
        if data[1] == '':
            return 'ok'
        return 'fail'
    return "fail"


def start():
    return appOp('start')


def stop():
    return appOp('stop')


def restart():
    return appOp('restart')


def reload():
    return appOp('reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status ' + getPluginName() + ' | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable ' + getPluginName())
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable ' + getPluginName())
    return 'ok'


def runLog():
    log_path = getServerDir() + '/log/doh.log'
    return log_path

def getTotalStatistics():
    st = status()
    data = {}
    if st.strip() == 'start':
        list_count = pQuery('select count(id) as num from repository')
        count = list_count[0]["num"]
        data['status'] = True
        data['count'] = count
        data['ver'] = mw.readFile(getServerDir() + '/version.pl').strip()
        return mw.returnJson(True, 'ok', data)

    data['status'] = False
    data['count'] = 0
    return mw.returnJson(False, 'fail', data)


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
    elif func == 'uninstall_pre_inspection':
        print(uninstallPreInspection())
    elif func == 'run_log':
        print(runLog())
    elif func == 'post_receive_log':
        print(postReceiveLog())
    elif func == 'conf':
        print(getConf())
    elif func == 'init_conf':
        print(getInitdConf())
    elif func == 'get_total_statistics':
        print(getTotalStatistics())
    else:
        print('fail')
