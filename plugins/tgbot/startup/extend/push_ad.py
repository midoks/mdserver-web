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

    # https://t.me/gjgzs2022 ｜ 19/m
    # ♻️CMS导航网♻️/💰流量变现💰 ｜ 28/m
    # CK资源采集 ｜29/m
    # https://zhaoziyuan.la/ | 15/m | 2m | next,7/15
    # 香港高防CDN ｜9/m
    # 🅾️代实名lDCApp +86接码全天在线 | 15/m
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="🅾️代实名lDCApp🙎‍♂️+86接码全天在线🅾️", url='https://t.me/ljh09852')
        ],
        [
            types.InlineKeyboardButton(
                text="香港高防CDN、免实名、试用30天", url='https://www.100dun.com')
        ],
        [
            types.InlineKeyboardButton(
                text="CK资源采集", url='https://ckzy1.com/')
        ],
        [
            types.InlineKeyboardButton(
                text="代付支付宝微信❤️淘宝帮付", url='https://t.me/Uxuanzhenpin')
        ],
        [
            types.InlineKeyboardButton(
                text="💰流量变现💰集团收量", url='https://t.me/taohaozhan')
        ],
        [
            types.InlineKeyboardButton(
                text="🙎‍♂️代实名🙍‍♀️过人脸🅾️国际阿里云腾讯云", url='https://t.me/gjgzs2022')
        ],
        [
            types.InlineKeyboardButton(
                text="倩倩CDN服务器", url='https://t.me/KLT_12'),
            types.InlineKeyboardButton(
                text="💎DigitalVirt(赞助商)", url='https://digitalvirt.com/aff.php?aff=154')
        ],
        [
            types.InlineKeyboardButton(
                text="论坛", url='https://bbs.midoks.me'),
            types.InlineKeyboardButton(
                text="搜索", url='https://bbs.midoks.me/search.php'),
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
