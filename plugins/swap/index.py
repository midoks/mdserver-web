# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'swap'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


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


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():
    data = mw.execShell("free -m|grep Swap|awk '{print $2}'")
    if data[0].strip() == '0':
        return 'stop'
    return 'start'


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # initd replace
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = content.replace(
            '{$SERVER_PATH}', getServerDir() + '/swapfile')
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/swap.service'
    systemServiceTpl = getPluginDir() + '/init.d/swap.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        swapon_bin = mw.execShell('which swapon')[0].strip()
        swapoff_bin = mw.execShell('which swapoff')[0].strip()
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        se_content = se_content.replace('{$SWAPON_BIN}', swapon_bin)
        se_content = se_content.replace('{$SWAPOFF_BIN}', swapoff_bin)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def swapOp(method):
    file = initDreplace()

    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' swap')
        if data[1] == '':
            return 'ok'
        return 'fail'

    data = mw.execShell(file + ' ' + method)
    if data[1] == '':
        return 'ok'
    return 'fail'


def start():
    return swapOp('start')


def stop():
    return swapOp('stop')


def restart():
    return swapOp('restart')


def reload():
    return 'ok'


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status swap | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable swap')
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable swap')
    return 'ok'


def swapStatus():
    sfile = getServerDir() + '/swapfile'

    if os.path.exists(sfile):
        size = os.path.getsize(sfile) / 1024 / 1024
    else:
        size = '218'
    data = {'size': size}
    return mw.returnJson(True, "ok", data)


def changeSwap():
    args = getArgs()
    data = checkArgs(args, ['size'])
    if not data[0]:
        return data[1]

    size = args['size']
    swapOp('stop')

    gsdir = getServerDir()

    cmd = 'dd if=/dev/zero of=' + gsdir + '/swapfile bs=1M count=' + size
    cmd += ' && mkswap ' + gsdir + '/swapfile && chmod 600 ' + gsdir + '/swapfile'
    msg = mw.execShell(cmd)
    swapOp('start')

    return mw.returnJson(True, "修改成功:\n" + msg[0])

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
    elif func == 'conf':
        print(getConf())
    elif func == "swap_status":
        print(swapStatus())
    elif func == "change_swap":
        print(changeSwap())
    else:
        print('error')
