# coding:utf-8

import sys
import io
import os
import time
import re
import json

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'webhook'


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


def getCfgFilePath():
    return getServerDir() + "/cfg.json"


def initCfg():
    cfg = getCfgFilePath()
    data = []
    mw.writeFile(cfg, json.dumps(data))


def getCfg():
    cfg = getCfgFilePath()
    if not os.path.exists(cfg):
        initCfg()

    data = mw.readFile(cfg)
    data = json.loads(data)
    return data


def addCfg(val):
    cfg = getCfgFilePath()
    data = getCfg()
    data.append(val)
    mw.writeFile(cfg, json.dumps(data))


def status():
    return 'start'


def addHook():
    args = getArgs()
    data = checkArgs(args, ['title', "shell"])
    if not data[0]:
        return data[1]

    hook = {}
    hook['title'] = args['title']
    hook['access_key'] = mw.getRandomString(48)
    hook['count'] = 0
    hook['addtime'] = int(time.time())
    hook['uptime'] = 0

    script_dir = getServerDir() + "/scripts"
    if not os.path.exists(script_dir):
        os.mkdir(script_dir)

    addCfg(hook)
    shellFile = script_dir + '/' + hook['access_key']
    mw.writeFile(shellFile, args['shell'])
    return mw.returnJson(True, '添加成功!')


def getList():
    data = getCfg()

    rdata = {}
    rdata['list'] = data
    rdata['script_dir'] = getServerDir() + "/scripts"
    return mw.returnJson(True, 'ok', rdata)


def getLog():
    args = getArgs()
    check_arg = checkArgs(args, ['path'])
    if not check_arg[0]:
        return check_arg[1]

    logPath = args['path']

    content = mw.getLastLine(logPath, 16)
    return mw.returnJson(True, 'ok', content)


def runShellArgs(args):
    data = getCfg()
    for i in range(len(data)):
        if data[i]['access_key'] == args['access_key']:
            script_dir = getServerDir() + "/scripts"
            shellFile = script_dir + '/' + args['access_key']
            param = args['params']
            if param == '':
                param = 'no-parameters'

            param = re.sub("\"", '', param)

            cmd = "bash {} {} >> {}.log 2>&1 &".format(
                shellFile, param, shellFile)
            # print(cmd)
            os.system(cmd)
            data[i]['count'] += 1
            data[i]['uptime'] = int(time.time())
            mw.writeFile(getCfgFilePath(), json.dumps(data))
            return mw.returnJson(True, '运行成功!')
    return mw.returnJson(False, '指定Hook不存在!')


def runShell():
    args = getArgs()
    check_arg = checkArgs(args, ['access_key'])
    if not check_arg[0]:
        return check_arg[1]

    args['params'] = 'panel-test'
    return runShellArgs(args)


def delHook():
    args = getArgs()
    check_arg = checkArgs(args, ['access_key'])
    if not check_arg[0]:
        return check_arg[1]

    data = getCfg()
    newdata = []
    for hook in data:
        if hook['access_key'] == args['access_key']:
            continue
        newdata.append(hook)

    jsonFile = getCfgFilePath()
    shellFile = getServerDir() + "/scripts/" + args['access_key']
    if not os.path.exists(shellFile):
        return mw.returnJson(False, '删除失败!')
    os.remove(shellFile)
    log_file = "{}.log".format(shellFile)
    if os.path.exists(log_file):
        os.remove(log_file)

    mw.writeFile(jsonFile, json.dumps(newdata))
    return mw.returnJson(True, '删除成功!')

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == "add_hook":
        print(addHook())
    elif func == "get_list":
        print(getList())
    elif func == "run_shell":
        print(runShell())
    elif func == 'del_hook':
        print(delHook())
    elif func == 'get_log':
        print(getLog())
    else:
        print('error')
