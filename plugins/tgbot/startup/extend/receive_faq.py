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


def isThisCmd(cmd, msg):
    clen = len(cmd)
    msg_len = len(msg)
    if msg_len < clen:
        return False

    check_msg = msg[0:clen]
    if cmd == check_msg:
        return True
    return False


def getReadCmd(cmd, msg):
    clen = len(cmd)
    msg_len = len(msg)
    real_msg = msg[clen:]
    return real_msg


def getFaqKw(cmd):
    matchObj = re.match(r'寻找【(.*?)】问题如下', cmd, re.M | re.I)
    data = matchObj.groups()
    if len(data) > 0:
        return True, data[0]
    return False, ''


def searchHttpPage(kw='', p=1, size=1):
    import urllib
    kw = kw.strip()
    kw = urllib.parse.quote_plus(kw)

    api = 'https://bbs.midoks.icu/plugin.php?id=external_api&f=bbs_search&q=' + kw + \
        '&size=' + str(size) + '&p=' + str(p)

    # print('url', api)
    data = mw.httpGet(api)
    # print(data)
    data = json.loads(data)
    # print(data)
    if data['code'] > -1:

        alist = data['data']['list']
        r = []
        for x in alist:
            tmp = {}
            tmp['tid'] = x['tid']
            tmp['subject'] = x['subject']
            tmp['url'] = 'https://bbs.midoks.icu/thread-' + \
                x['tid'] + '-1-1.html'
            r.append(tmp)
        data['data']['list'] = r
    return data


def searchFaq(bot, message, cmd_text):
    # cmd_text = 'mw'
    data = searchHttpPage(cmd_text, 1, 5)
    if data['code'] == 0 and len(data['data']['list']) > 0:
        keyboard = []

        dlist = data['data']['list']
        for x in dlist:
            keyboard.append([types.InlineKeyboardButton(
                text=x['subject'], url=x['url'])])

        keyboard.append([
            types.InlineKeyboardButton(
                text="下一页", callback_data='bbs_next_page_2'),
            types.InlineKeyboardButton(
                text="第" + str(data['data']['p']) + "页,共" + str(data['data']['page_num']) + "页", callback_data='bbs_page_total')
        ])

        keyboard.append([types.InlineKeyboardButton(
            text="关闭消息", callback_data='bbs_search_close')])

        # print(keyboard)
        markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(message.chat.id, "寻找【" +
                         cmd_text.strip() + "】问题如下:", reply_markup=markup)
    else:
        keyboard = [
            [
                types.InlineKeyboardButton(
                    text="论坛", url='https://bbs.midoks.icu'),
                types.InlineKeyboardButton(
                    text="搜索", url='https://bbs.midoks.icu/search.php')
            ],
            [
                types.InlineKeyboardButton(
                    text="关闭消息", callback_data='bbs_search_close')
            ]

        ]
        markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(
            message.chat.id, "未找到合适内容,请在官方论坛[bbs.midoks.icu]提问!", reply_markup=markup)

    return True


def searchDebug(bot, message, cmd_text):
    searchFaq(bot, message, cmd_text)
    return True


def answer_callback_query(bot, call):

    keyword = call.data

    if keyword == 'bbs_search_close':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        return

    is_bbs_page = False
    p = 1
    if keyword.startswith('bbs_next_page'):
        is_bbs_page = True
        p = keyword.replace('bbs_next_page_', '')

    if keyword.startswith('bbs_pre_page'):
        is_bbs_page = True
        p = keyword.replace('bbs_pre_page_', '')

    # print("p", p)
    if is_bbs_page:
        is_match, cmd_text = getFaqKw(call.message.text)
        if not is_match:
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id, text="出现错误!")
            return

        data = searchHttpPage(cmd_text, int(p), 5)

        dlist = data['data']['list']
        # print(data)
        keyboard = []
        for x in dlist:
            keyboard.append([types.InlineKeyboardButton(
                text=x['subject'], url=x['url'])])

        page_nav = []
        if int(data['data']['p']) > 1:
            page_nav.append(types.InlineKeyboardButton(
                text="上一页", callback_data='bbs_pre_page_' + str(int(p) - 1)))

        if data['data']['page_num'] != data['data']['p']:
            page_nav.append(types.InlineKeyboardButton(
                text="下一页", callback_data='bbs_next_page_' + str(int(p) + 1)))

        page_nav.append(types.InlineKeyboardButton(
            text="第" + str(data['data']['p']) + "页,共" + str(data['data']['page_num']) + "页", callback_data='bbs_page_total'))

        keyboard.append(page_nav)

        keyboard.append([types.InlineKeyboardButton(
            text="关闭消息", callback_data='bbs_search_close')])

        markup = types.InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=call.message.text, reply_markup=markup)


def run(bot, message):
    text_body = message.text

    # 过滤URL
    is_has_url = re.search(
        '(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', text_body)
    if is_has_url:
        return bot

    # print(text_body)
    if isThisCmd('/?:', text_body):
        cmd_text = getReadCmd('/?:', text_body)
        cmd_text = cmd_text.strip().strip(":")
        if cmd_text == "":
            return bot.send_message(message.chat.id, "搜索内容不能为空, 例如:/?: 数据库")
        return searchFaq(bot, message, cmd_text)

    if isThisCmd('/faq', text_body):
        cmd_text = getReadCmd('/faq', text_body)
        cmd_text = cmd_text.strip().strip(":")
        if cmd_text == "":
            return bot.send_message(message.chat.id, "搜索内容不能为空, 例如:/faq 数据库")
        return searchFaq(bot, message, cmd_text)

    return bot


if __name__ == "__main__":
    # print(isThisCmd('/?:', '/?:如何在安装面板'))
    # print(getReadCmd('/?:', '/?:如何在安装面板'))
    # print(searchHttpPage('mw'))
    print(getFaqKw('寻找【mw】问题如下:'))
