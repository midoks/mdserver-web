# coding:utf-8

import sys
import io
import os
import time
import re
import json
import base64
import threading

sys.path.append(os.getcwd() + "/class/core")
import mw

import telebot


def getPluginName():
    return 'tgbot'


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
    log_file = getServerDir() + '/push.log'
    mw.writeFileLog(now + ':' + log_str, log_file, limit_size=5 * 1024)
    return True

# start tgbot
cfg = getConfigData()
while True:
    cfg = getConfigData()
    if 'bot' in cfg and 'app_token' in cfg['bot']:
        if cfg['bot']['app_token'] != '' and cfg['bot']['app_token'] != 'app_token':
            break
    writeLog('等待输入配置,填写app_token')
    time.sleep(3)


bot = telebot.TeleBot(cfg['bot']['app_token'])


def runBotPushTask():
    plist = getStartExtCfgByTag('push')
    for p in plist:
        try:
            script = p['name'].split('.')[0]
            __import__(script).run(bot)
        except Exception as e:
            writeLog('-----runBotPushTask error start -------')
            writeLog(mw.getTracebackInfo())
            writeLog('-----runBotPushTask error end -------')


def botPush():
    while True:
        runBotPushTask()
        time.sleep(1)


def runBotPushOtherTask():
    plist = getStartExtCfgByTag('other')
    for p in plist:
        try:
            script = p['name'].split('.')[0]
            __import__(script).run(bot)
        except Exception as e:
            writeLog('-----runBotPushOtherTask error start -------')
            writeLog(mw.getTracebackInfo())
            writeLog('-----runBotPushOtherTask error end -------')


def botPushOther():
    while True:
        runBotPushOtherTask()
        time.sleep(1)


if __name__ == "__main__":

    # 机器人推送任务
    botPushTask = threading.Thread(target=botPush)
    botPushTask.start()

    # 机器人其他推送任务
    botPushOtherTask = threading.Thread(target=botPushOther)
    botPushOtherTask.start()
