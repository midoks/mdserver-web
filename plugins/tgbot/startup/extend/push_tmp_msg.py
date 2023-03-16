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
from telebot import types
from telebot.util import quick_markup

# 广告推送实例


chat_id = -1001578009023
# chat_id = 5568699210


def send_msg(bot, tag='ad', trigger_time=300):
    # 信号只在一个周期内执行一次|start
    lock_file = mw.getServerDir() + '/tgbot/lock.json'
    if not os.path.exists(lock_file):
        mw.writeFile(lock_file, '{}')

    lock_data = json.loads(mw.readFile(lock_file))
    if tag in lock_data:
        diff_time = time.time() - lock_data[tag]['do_time']
        if diff_time >= trigger_time:
            lock_data[tag]['do_time'] = time.time()
        else:
            return False, 0, 0
    else:
        lock_data[tag] = {'do_time': time.time()}
    mw.writeFile(lock_file, json.dumps(lock_data))
    # 信号只在一个周期内执行一次|end

    keyboard = [
        [
            types.InlineKeyboardButton(
                text="为了不打扰双方，私聊解决问题先转100U，否则无视!", url='tg://user?id=5568699210')
        ],
        [
            types.InlineKeyboardButton(
                text="论坛", url='https://bbs.midoks.me'),
            types.InlineKeyboardButton(
                text="搜索", url='https://bbs.midoks.me/search.php')
        ]
    ]

    msg = bot.send_message(
        chat_id, "由于在解决的问题的时候，不给信息，无法了解情况。以后不再群里回答技术问题。全部去论坛提问。为了让群里都知晓。轮播一个月", reply_markup=markup)

    # print(msg.message_id)
    time.sleep(1 * 60)
    del_msg = bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    # print(del_msg)


def run(bot):
    send_msg(bot, 'ad', 5 * 60)
