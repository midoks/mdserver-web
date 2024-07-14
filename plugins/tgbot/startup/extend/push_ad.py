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

    # https://t.me/gjgzs2022 ｜ 22/m | @GJ_gzs
    # https://zhaoziyuan1.cc | web | 15/m | 2m | next,9/15 ｜ @baleite
    # 综合包网/NG接口开户 | 28/m | 6m | next,10/28 | @aabbcx888
    # 实名认证/过人脸🕵️‍♀️各种账号处理✅ | 30/m| next,12/30 | @nngzs
    # 桃花资源采集| 13/m| next,1/13 | @xiaolizi1122
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="桃花资源采集🚀 ", url='https://thzy.me')
        ],
        [
            types.InlineKeyboardButton(
                text="👑 综合包网/NG接口开户", url='https://t.me/NG_Tony')
        ],
        [
            types.InlineKeyboardButton(
                text="实卡接码🙎‍♂️代实名/过人脸🅾️开飞机会员", url='https://t.me/gjgzs2022')
        ],
        # [
        #     types.InlineKeyboardButton(
        #         text="🚀腾云机场|解锁流媒体和ChatGPT", url='https://www.tencloud.net/index.php#/register?code=OGvXSTsc')
        # ],
        [
            types.InlineKeyboardButton(
                text="实名认证/过人脸🕵️‍♀️各种账号处理✅", url='https://t.me/niuniu234')
        ],
        [
            types.InlineKeyboardButton(
                text="官网", url='https://github.com/midoks/mdserver-web'),
            types.InlineKeyboardButton(
                text="💎DigitalVirt(赞助商)", url='https://digitalvirt.com/aff.php?aff=154')
        ],
        [
            types.InlineKeyboardButton(
                text="论坛", url='https://bbs.midoks.icu'),
            types.InlineKeyboardButton(
                text="搜索", url='https://bbs.midoks.icu/search.php'),
            types.InlineKeyboardButton(
                text="@ME", url='tg://user?id=5568699210'),
            types.InlineKeyboardButton(
                text="100RMB/M", url='tg://user?id=5568699210')
        ]
    ]
    markup = types.InlineKeyboardMarkup(keyboard)
    image_file = mw.getPluginDir() + '/tgbot/static/image/ad.png'

    telebot_image = telebot.types.InputFile(image_file)
    msg = bot.send_photo(chat_id, telebot_image, reply_markup=markup)

    # print(msg.message_id)
    time.sleep(5 * 60)
    del_msg = bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    # print(del_msg)


def run(bot):
    send_msg(bot, 'ad', 1 * 60 * 60)
