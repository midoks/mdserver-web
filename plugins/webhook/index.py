# coding:utf-8

import sys
import io
import os
import time
import re
import hmac
import json
import secrets
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
    return 'webhook'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getCfgFilePath():
    return getServerDir() + "/cfg.json"


ACCESS_KEY_RE = re.compile(r'^[a-f0-9]{64}$')


def genAccessKey():
    # 使用 CSPRNG 生成不可猜测的密钥
    return secrets.token_hex(32)


def migrateCfg(data):
    # 兼容旧版本: 旧 access_key 为 md5(title), 可被猜测, 自动迁移为随机密钥
    changed = False
    script_dir = getServerDir() + '/scripts'
    for hook in data:
        if not isinstance(hook, dict):
            continue
        key = hook.get('access_key', '')
        if ACCESS_KEY_RE.fullmatch(key or ''):
            continue
        if not hook.get('title'):
            continue
        new_key = genAccessKey()
        try:
            old_script = script_dir + '/' + key
            new_script = script_dir + '/' + new_key
            if key and os.path.exists(old_script):
                os.rename(old_script, new_script)
            if key and os.path.exists(old_script + '.log'):
                os.rename(old_script + '.log', new_script + '.log')
        except Exception:
            pass
        hook['access_key'] = new_key
        changed = True
    if changed:
        mw.writeFile(getCfgFilePath(), json.dumps(data))
    return data


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
    return migrateCfg(data)


def addCfg(val):
    cfg = getCfgFilePath()
    data = getCfg()
    data.append(val)
    mw.writeFile(cfg, json.dumps(data))


def status():
    return 'start'


def addHook():
    args = mw.getPluginArgs()
    data = mw.checkPluginArgs(args, ['title', "shell"])
    if not data[0]:
        return data[1]

    hook = {}
    hook['title'] = args['title']
    if hook['title'] == '':
        return mw.returnJson(False, '名称不能为空!')

    hook['access_key'] = genAccessKey()
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

def addHookShell(args):
    if args['title'] == '':
        return mw.returnJson(False, '名称不能为空!')

    hook = {}
    hook['title'] = args['title']
    hook['access_key'] = genAccessKey()
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
    args = mw.getPluginArgs()
    check_arg = mw.checkPluginArgs(args, ['path'])
    if not check_arg[0]:
        return check_arg[1]

    logPath = args['path']

    content = mw.getLastLine(logPath, 500)
    return mw.returnJson(True, 'ok', content)

def getLogCb(args):
    # print(args)
    logPath = args['path']
    content = mw.getLastLine(logPath, 3000)
    return mw.returnData(True, 'ok', content)


def runShellArgs(args):
    data = getCfg()
    for i in range(len(data)):
        key = data[i].get('access_key', '')
        if key and hmac.compare_digest(str(key), str(args.get('access_key', ''))):
            script_dir = getServerDir() + "/scripts"
            shellFile = script_dir + '/' + key
            param = args.get('params', '')
            if param == '':
                param = 'no-parameters'

            # 参数作为单个 argv 传给 bash, 不经过 shell, 避免命令注入
            log_file = shellFile + '.log'
            with open(log_file, 'ab') as logf:
                subprocess.Popen(['bash', shellFile, param],
                                 stdout=logf, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            data[i]['count'] += 1
            data[i]['uptime'] = int(time.time())
            mw.writeFile(getCfgFilePath(), json.dumps(data))
            return mw.returnJson(True, '运行成功!')
    return mw.returnJson(False, '指定Hook不存在!')

def getRunShellCmd():
    args = mw.getPluginArgs()
    check_arg = mw.checkPluginArgs(args, ['access_key'])
    if not check_arg[0]:
        return check_arg[1]

    access_key = args['access_key']
    if not ACCESS_KEY_RE.fullmatch(access_key or ''):
        return mw.returnJson(False, '非法的Hook密钥!')

    script_dir = getServerDir() + "/scripts"
    shellFile = script_dir + '/' + access_key
    param = ''
    if 'params' in args:
        param = args['params']

    cmd = ""
    cmd += "git config --global credential.helper store\n"
    cmd += "git config --global pull.rebase false\n"
    cmd += "bash " + mw.quote(shellFile)
    if param != '':
        cmd += " " + mw.quote(param)
    return mw.returnJson(True, 'ok', cmd)


def runShell():
    args = mw.getPluginArgs()
    check_arg = mw.checkPluginArgs(args, ['access_key'])
    if not check_arg[0]:
        return check_arg[1]

    args['params'] = 'panel-test'
    return runShellArgs(args)


def delHook():
    args = mw.getPluginArgs()
    check_arg = mw.checkPluginArgs(args, ['access_key'])
    if not check_arg[0]:
        return check_arg[1]

    access_key = args['access_key']
    if not ACCESS_KEY_RE.fullmatch(access_key or ''):
        return mw.returnJson(False, '非法的Hook密钥!')

    data = getCfg()
    newdata = []
    for hook in data:
        if hook['access_key'] == access_key:
            continue
        newdata.append(hook)

    jsonFile = getCfgFilePath()
    shellFile = getServerDir() + "/scripts/" + access_key
    if not os.path.exists(shellFile):
        return mw.returnJson(False, '删除失败!')
    os.remove(shellFile)
    log_file = "{}.log".format(shellFile)
    if os.path.exists(log_file):
        os.remove(log_file)

    mw.writeFile(jsonFile, json.dumps(newdata))
    return mw.returnJson(True, '删除成功!')


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    return content


def configTpl():
    path = getPluginDir() + '/tpl'
    pathFile = os.listdir(path)
    tmp = []
    for one in pathFile:
        file = path + '/' + one
        tmp.append(file)
    return mw.getJson(tmp)

def readConfigTpl():
    args = mw.getPluginArgs()
    data = mw.checkPluginArgs(args, ['file', 'title'])
    if not data[0]:
        return data[1]

    if args['title'] == '':
        return mw.returnJson(False, '名称不能为空!')

    content = mw.readFile(args['file'])
    content = contentReplace(content)

    content = content.replace('{$REPO}', args['title'])
    content = content.replace('{$REPO_NAME}', mw.md5(args['title']))

    return mw.returnJson(True, 'ok', content)

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
    elif func == 'run_shell_cmd':
        print(getRunShellCmd())
    elif func == 'del_hook':
        print(delHook())
    elif func == 'get_log':
        print(getLog())
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    else:
        print('error')
