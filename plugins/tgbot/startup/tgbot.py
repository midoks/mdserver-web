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
    log_file = getServerDir() + '/task.log'
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


init_list = getStartExtCfgByTag('init')
for p in init_list:
    try:
        script = p['name'].split('.')[0]
        __import__(script).init(bot)
    except Exception as e:
        writeLog('-----init error start -------')
        writeLog(mw.getTracebackInfo())
        writeLog('-----init error end -------')


@bot.message_handler(commands=['chat_id'])
def hanle_get_chat_id(message):
    bot.reply_to(message, message.chat.id)


@bot.message_handler(func=lambda message: True)
def all_message(message):
    rlist = getStartExtCfgByTag('receive')
    for r in rlist:
        try:
            script = r['name'].split('.')[0]
            __import__(script).run(bot, message)
        except Exception as e:
            writeLog('-----all_message error start -------')
            writeLog(mw.getTracebackInfo())
            writeLog('-----all_message error end -------')


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    rlist = getStartExtCfgByTag('receive')
    for r in rlist:
        try:
            script = r['name'].split('.')[0]
            __import__(script).answer_callback_query(bot, call)
        except Exception as e:
            writeLog('-----callback_query_handler error start -------')
            writeLog(mw.getTracebackInfo())
            writeLog('-----callback_query_handler error end -------')


def runBot(bot):
    try:
        bot.polling()
    except Exception as e:
        writeLog('-----runBot error start -------')
        writeLog(str(e))
        writeLog('-----runBot error end -------')
        time.sleep(1)
        runBot(bot)

if __name__ == "__main__":

    writeLog('启动成功')
    runBot(bot)


# asyncio.run(bot.polling())
