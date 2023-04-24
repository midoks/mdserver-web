# coding:utf-8

import sys
import io
import os
import time
import re
import json
import base64
import threading

# python /Users/midoks/Desktop/mwdev/server/tgclient/tgclient.py
# python /www/server/tgclient/tgclient.py

from telethon import TelegramClient


sys.path.append(os.getcwd() + "/class/core")
import mw


def getPluginName():
    return 'tgclient'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


sys.path.append(getServerDir() + "/extend")


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


def getStartExtCfgByTag(tag='push'):
    # 获取开启的扩展
    elist = getExtCfg()
    rlist = []
    for x in elist:
        if x['tag'] == tag and x['status'] == 'start':
            rlist.append(x)
    return rlist


def writeLog(log_str):
    if __name__ == "__main__":
        print(log_str)

    now = mw.getDateFromNow()
    log_file = getServerDir() + '/task.log'
    mw.writeFileLog(now + ':' + log_str, log_file, limit_size=5 * 1024)
    return True


# start tgbot
cfg = getConfigData()
while True:
    cfg = getConfigData()
    if 'bot' in cfg and 'api_id' in cfg['bot']:
        if cfg['bot']['api_id'] != '' and cfg['bot']['api_id'] != 'api_id':
            break
        if cfg['bot']['api_hash'] != '' and cfg['bot']['api_hash'] != 'api_hash':
            break
    writeLog('等待输入配置,填写app_token')
    time.sleep(3)

client = TelegramClient('mdioks', cfg['bot']['api_id'], cfg['bot']['api_hash'])

async def main():
    # Now you can use all client methods listed below, like for example...
    await client.send_message('me', 'Hello to myself!')

with client:
    client.loop.run_until_complete(main())
