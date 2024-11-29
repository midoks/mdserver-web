# coding:utf-8

import sys
import io
import os
import time
import re
import json

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'fail2ban'

def f2bDir():
    return '/run/'+getPluginName()

def f2bEtcDir():
    return '/etc/'+getPluginName()

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
    path = f2bEtcDir() + "/fail2ban.conf"
    return path


def getConfTpl():
    path = getPluginDir() + "/tpl/fail2ban.conf"
    return path


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

def configTpl():
    path = f2bEtcDir()
    pathFile = os.listdir(path)
    tmp = []
    for one in pathFile:
        if one.endswith("conf"):
            file = path + '/' + one
            tmp.append(file)
    return mw.getJson(tmp)


def readConfigTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]

    content = mw.readFile(args['file'])
    content = contentReplace(content)
    return mw.returnJson(True, 'ok', content)

def runLog():
    return '/var/log/fail2ban.log'

def getPidFile():
    f2dir = f2bDir()
    return f2dir+'/fail2ban.pid'

def status():
    pid_file = getPidFile()
    if not os.path.exists(pid_file):
        return 'stop'
    return 'start'

def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    return content


def initFail2BanD():
    dst_conf = f2bEtcDir() + '/fail2ban.d/default.conf'
    dst_conf_tpl = getPluginDir() + '/tpl/fail2ban.d/default.conf'
    if not os.path.exists(dst_conf):
        content = mw.readFile(dst_conf_tpl)
        content = contentReplace(content)
        mw.writeFile(dst_conf, content)

def initJailD():
    dst_conf = f2bEtcDir() + '/jail.d/default.conf'
    dst_conf_tpl = getPluginDir() + '/tpl/jail.d/default.conf'
    if not os.path.exists(dst_conf):
        content = mw.readFile(dst_conf_tpl)
        content = contentReplace(content)
        mw.writeFile(dst_conf, content)

def initDreplace():

    file_tpl = getInitDTpl()
    service_path = mw.getServerDir()

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # config replace
    # dst_conf = getConf()
    # dst_conf_init = getServerDir() + '/init.pl'
    # if not os.path.exists(dst_conf_init):
    #     content = mw.readFile(getConfTpl())
    #     content = contentReplace(content)
    #     mw.writeFile(dst_conf, content)
    #     mw.writeFile(dst_conf_init, 'ok')

    initFail2BanD()
    initJailD()

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/' + getPluginName() + '.service'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/' + getPluginName() + '.service.tpl'
        content = mw.readFile(systemServiceTpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def f2bOp(method):
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
    return f2bOp('start')


def stop():
    return f2bOp('stop')


def restart():
    status = f2bOp('restart')

    log_file = runLog()
    mw.execShell("echo '' > " + log_file)
    return status


def reload():
    return f2bOp('reload')


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


# 读取配置
def _read_conf(path, l=None):
    conf = mw.readFile(path)
    if not conf:
        if not l:
            conf = {}
        else:
            conf = []
        mw.writeFile(path, json.dumps(conf))
        return conf
    return json.loads(conf)

def getBlackFile():
    return getServerDir() + "/black_list.json"


def getConfigFile():
    return getServerDir() + "/config.json"


def getBlackListArr():
    _black_list = getBlackFile()
    conf = _read_conf(_black_list, l=1)
    if not conf:
        conf = []
    return conf


def getBlackList():
    conf = getBlackListArr()
    content = "\n".join(conf)
    return mw.returnJson(True, 'ok', content)

def setBlackIp():
    ip_list = getBlackListArr()

    args = getArgs()
    data = checkArgs(args, ['black_ip'])
    if not data[0]:
        return data[1]

    new_ip_list = args['black_ip']
    add_ip_list = [new_ip for new_ip in new_ip_list if new_ip not in ip_list]
    del_ip_list = [del_ip for del_ip in ip_list if del_ip not in new_ip_list]
    rep_ip = "^(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)(\\.(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)){3}($|[\\/\\d]+$)"
    rep_ipv6 = "^\\s*((([0-9A-Fa-f]{1,4}:){7}(([0-9A-Fa-f]{1,4})|:))|(([0-9A-Fa-f]{1,4}:){6}(:|((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})|(:[0-9A-Fa-f]{1,4})))|(([0-9A-Fa-f]{1,4}:){5}((:((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){4}(:[0-9A-Fa-f]{1,4}){0,1}((:((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){3}(:[0-9A-Fa-f]{1,4}){0,2}((:((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){2}(:[0-9A-Fa-f]{1,4}){0,3}((:((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:)(:[0-9A-Fa-f]{1,4}){0,4}((:((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(:(:[0-9A-Fa-f]{1,4}){0,5}((:((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(((25[0-5]|2[0-4]\\d|[01]?\\d{1,2})(\\.(25[0-5]|2[0-4]\\d|[01]?\\d{1,2})){3})))(%.+)?\\s*$"
    
    data = _read_conf(getConfigFile())

    if new_ip_list == '':
        for d in data:
            for ip in ip_list:
                mw.execShell('fail2ban-client -vvv set {jail} unbanip {ip}'.format(jail=d, ip=ip))

        mw.writeFile(getBlackFile(), json.dumps([]))
        return nw.returnJson(True, "禁止IP成功")

    # 检查IP格式
    for ip in add_ip_list:
        if not re.search(rep_ip, ip) and not re.search(rep_ipv6, ip):
            return mw.returnJson(False, "IP格式错误 {}".format(ip))

    # 添加新域名到黑名单
    for d in data:
        for ip in add_ip_list:
            mw.execShell('fail2ban-client -vvv set {jail} banip {ip}'.format(jail=d, ip=ip))

    # 检查是否有清理掉的IP
    for d in data:
        for ip in del_ip_list:
            mw.execShell('fail2ban-client -vvv set {jail} unbanip {ip}'.format(jail=d, ip=ip))

    for ip in add_ip_list:
        ip_list.append(ip)

    mw.writeFile(getBlackFile(), json.dumps(ip_list))
    return mw.returnJson(True, "添加黑名单成功")

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
    elif func == 'run_log':
        print(runLog())
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    elif func == 'get_black_list':
        print(getBlackList())
    elif func == 'set_black_ip':
        print(setBlackIp())
    else:
        print('error')
