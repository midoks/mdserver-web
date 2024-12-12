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
    return 'webhook'

def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getCfgFilePath():
    return getServerDir() + "/cfg.json"


def getCfg():
    cfg = getCfgFilePath()
    if not os.path.exists(cfg):
        initCfg()

    data = mw.readFile(cfg)
    data = json.loads(data)
    return data


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
