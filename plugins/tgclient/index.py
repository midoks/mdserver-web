# coding:utf-8

import sys
import io
import os
import time
import re
import json
import base64

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'tgclient'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConfigData():
    cfg_path = getServerDir() + "/data.cfg"
    if not os.path.exists(cfg_path):
        mw.writeFile(cfg_path, '{}')
    t = mw.readFile(cfg_path)
    return json.loads(t)


def writeConf(data):
    cfg_path = getServerDir() + "/data.cfg"
    mw.writeFile(cfg_path, json.dumps(data))
    return True


def getExtCfg():
    cfg_path = getServerDir() + "/extend.cfg"
    if not os.path.exists(cfg_path):
        mw.writeFile(cfg_path, '{}')
    t = mw.readFile(cfg_path)
    return json.loads(t)


def writeExtCfg(data):
    cfg_path = getServerDir() + "/extend.cfg"
    return mw.writeFile(cfg_path, json.dumps(data))


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


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
    data = mw.execShell(
        "ps -ef|grep tgclient |grep -v grep  | grep -v mdserver-web | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = mw.getServerDir()
    app_path = service_path + '/' + getPluginName()

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # initd replace
    # if not os.path.exists(file_bin):
    content = mw.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path + '/mdserver-web')
    content = content.replace('{$APP_PATH}', app_path)

    mw.writeFile(file_bin, content)
    mw.execShell('chmod +x ' + file_bin)

    pyMainTplContent = mw.readFile(getPluginDir() + '/startup/tgclient.py')
    toPyMainPath = mw.getServerDir() + '/tgclient.py'
    mw.writeFile(toPyMainPath, pyMainTplContent)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/tgclient.service'
    systemServiceTpl = getPluginDir() + '/init.d/tgclient.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$APP_PATH}', app_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def tbOp(method):
    file = initDreplace()

    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell(file + ' ' + method)
    # print(data)
    if data[1] == '':
        return 'ok'
    return 'ok'


def start():
    return tbOp('start')


def stop():
    return tbOp('stop')


def restart():
    status = tbOp('restart')
    return status


def reload():

    tgbot_tpl = getPluginDir() + '/startup/tgclient.py'
    tgbot_dst = getServerDir() + '/tgclient.py'

    content = mw.readFile(tgbot_tpl)
    mw.writeFile(tgbot_dst, content)

    ext_src = getPluginDir() + '/startup/extend'
    ext_dst = getServerDir()

    mw.execShell('cp -rf ' + ext_src + ' ' + ext_dst)

    return tbOp('restart')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status ' + \
        getPluginName() + ' | grep loaded | grep "enabled;"'
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


def getClientConf():
    data = getConfigData()
    if 'bot' in data:
        return mw.returnJson(True, 'ok', data['bot'])
    return mw.returnJson(False, 'ok', {})


def setClientConf():
    args = getArgs()
    data_args = checkArgs(args, ['api_id', 'api_hash'])
    if not data_args[0]:
        return data_args[1]

    data = getConfigData()
    args['api_id'] = base64.b64decode(args['api_id']).decode('ascii')
    args['api_hash'] = base64.b64decode(args['api_hash']).decode('ascii')
    data['bot'] = args
    writeConf(data)

    return mw.returnJson(True, '保存成功!', [])


def installPreInspection():
    i = sys.version_info
    if i[0] < 3 or i[1] < 7:
        return "telebot在python小于3.7无法正常使用"
    return 'ok'


def uninstallPreInspection():
    stop()
    return "请手动删除<br/> rm -rf {}".format(getServerDir())


def getExtCfgByName(name):
    elist = getExtCfg()
    for x in elist:
        if x['name'] == name:
            return x
    return None


def clientExtList():

    args = getArgs()
    data_args = checkArgs(args, ['p'])
    if not data_args[0]:
        return data_args[1]

    ext_path = getServerDir() + '/extend'
    if not os.path.exists(ext_path):
        return mw.returnJson(False, 'ok', [])
    elist_source = os.listdir(ext_path)

    elist = []
    for e in elist_source:
        if e.endswith('py'):
            elist.append(e)

    page = int(args['p'])
    page_size = 5

    make_ext_list = []
    for ex in elist:
        tmp = {}
        tmp['name'] = ex
        edata = getExtCfgByName(ex)
        if edata:
            tmp['status'] = edata['status']
        else:
            tmp['status'] = 'stop'

        tmp['tag'] = ex.split('_')[0]
        make_ext_list.append(tmp)

    writeExtCfg(make_ext_list)
    dlist_sum = len(make_ext_list)

    page_start = int((page - 1) * page_size)
    page_end = page_start + page_size

    if page_end >= dlist_sum:
        ret_data = make_ext_list[page_start:]
    else:
        ret_data = make_ext_list[page_start:page_end]

    data = {}
    data['data'] = ret_data
    data['args'] = args
    data['list'] = mw.getPage(
        {'count': dlist_sum, 'p': page, 'row': page_size, 'tojs': 'botExtListP'})

    return mw.returnJson(True, 'ok', data)


def setExtStatus():
    args = getArgs()
    data_args = checkArgs(args, ['name', 'status'])
    if not data_args[0]:
        return data_args[1]

    elist = getExtCfg()
    name = args['name']
    status = args['status']
    for x in range(len(elist)):
        if elist[x]['name'] == name:
            elist[x]['status'] = status
            break

    writeExtCfg(elist)

    action = '开启'
    if status == 'stop':
        action = '关闭'

    return mw.returnJson(True, action + '[' + name + ']扩展成功')


def runLog():
    p = getServerDir() + '/task.log'
    return p


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
    elif func == 'get_client_conf':
        print(getClientConf())
    elif func == 'set_client_conf':
        print(setClientConf())
    elif func == 'client_ext_list':
        print(clientExtList())
    elif func == 'set_ext_status':
        print(setExtStatus())
    elif func == 'run_log':
        print(runLog())

    else:
        print('error')
