
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

import telebot


def getPluginName():
    return 'tgbot'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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


def writeLog(log_str):
    if __name__ == "__main__":
        print(log_str)

    log_file = getServerDir() + '/task.log'
    mw.writeFileLog(log_str, log_file, limit_size=5 * 1024)
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


# from telebot.async_telebot import AsyncTeleBot
# import asyncio
# bot = AsyncTeleBot(cfg['bot']['app_token'])


@bot.message_handler(commands=['start', 'help'])
def hanle_start_help(message):
    bot.reply_to(message, "hello world")


@bot.message_handler(commands=['chat_id'])
def hanle_get_chat_id(message):
    bot.reply_to(message, message.chat.id)

writeLog('启动成功')
bot.polling()
# asyncio.run(bot.polling())
