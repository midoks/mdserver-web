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


def initCfg():
    mw.writeFile(getCfgFilePath(), json.dumps([]))


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


def getCfg():
    cfg = getCfgFilePath()
    if not os.path.exists(cfg):
        initCfg()

    data = mw.readFile(cfg)
    data = json.loads(data)
    return migrateCfg(data)


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
