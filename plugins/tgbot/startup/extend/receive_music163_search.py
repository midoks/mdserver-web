# coding:utf-8

import sys
import io
import os
import time
import re
import json
import base64
import threading


import telebot
from telebot import types
from telebot.util import quick_markup

# 网易音乐搜索


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


def httpPost(url, data, timeout=10):
    """
    发送POST请求
    @url 被请求的URL地址(必需)
    @data POST参数，可以是字符串或字典(必需)
    @timeout 超时时间默认60秒
    return string
    """
    try:
        import urllib.request
        import ssl
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data)
        response = urllib.request.urlopen(req, timeout=timeout)
        result = response.read()
        if type(result) == bytes:
            result = result.decode('utf-8')
        return result
    except Exception as ex:
        return str(ex)


def musicSearch(kw, page=1, page_size=5):
    m_offset = (int(page) - 1) * int(page_size)
    data = httpPost('http://music.163.com/api/cloudsearch/pc', {
        's': kw,
        'type': '1',
        'total': 'true',
        'limit': page_size,
        'offset': m_offset,
    })
    # data_a = json.loads(data)
    # print(data)
    return json.loads(data)


def musicSongD(mid):
    data = httpPost('http://music.163.com/api/v3/song/detail/', {
        'c': '[{"id":' + str(mid) + ',"v":0}]',
    })
    # print(data)
    return json.loads(data)


def musicSongDataUrl(mid):
    data = httpPost('http://music.163.com/api/song/enhance/player/url', {
        'br': 320 * 1000,
        'ids': [mid],
    })
    return json.loads(data)


def writeLog(log_str):
    if __name__ == "__main__":
        print(log_str)

    now = mw.getDateFromNow()
    log_file = mw.getServerDir() + '/tgbot/task.log'
    mw.writeFileLog(now + ':' + log_str, log_file, limit_size=5 * 1024)
    return True


def tgSearchMusic_t(cmd_text):
    data = musicSearch(cmd_text, 1, 5)

    if data['code'] == 200 and len(data['result']['songs']) > 0:
        slist = data['result']['songs']
        print(s)
    else:
        keyboard = [
            [
                types.InlineKeyboardButton(
                    text="论坛", url='https://bbs.midoks.me'),
                types.InlineKeyboardButton(
                    text="搜索", url='https://bbs.midoks.me/search.php')
            ],
            [
                types.InlineKeyboardButton(
                    text="关闭消息", callback_data='bbs_search_close')
            ]

        ]
        markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(
            message.chat.id, "未找到合适内容,请在官方论坛[bbs.midoks.me]提问!", reply_markup=markup)
    return True


def tgSearchMusic(bot, message, cmd_text):
    import math
    data = musicSearch(cmd_text, 1, 5)
    if data['code'] == 200 and len(data['result']['songs']) > 0:
        keyboard = []
        slist = data['result']['songs']
        page_total = math.ceil(data['result']['songCount'] / 5)

        for x in slist:
            keyboard.append([types.InlineKeyboardButton(
                text=x['name'], callback_data='m163:' + str(x['id']))])

        keyboard.append([
            types.InlineKeyboardButton(
                text="下一页", callback_data='m163_next_page_2'),
            types.InlineKeyboardButton(
                text="第1页,共" + str(page_total) + "页", callback_data='m163_page_total')
        ])

        keyboard.append([types.InlineKeyboardButton(
            text="关闭消息", callback_data='m163_search_close')])

        # print(keyboard)
        markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(message.chat.id, "寻找【" +
                         cmd_text.strip() + "】歌曲如下:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "未找到合适内容")
    return True


def getFaqKw(cmd):
    matchObj = re.match(r'寻找【(.*?)】歌曲如下', cmd, re.M | re.I)
    data = matchObj.groups()
    if len(data) > 0:
        return True, data[0]
    return False, ''


def answer_callback_query(bot, call):
    import math
    keyword = call.data
    print(keyword)
    if keyword == 'm163_search_close':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        return

    is_m163_page = False
    p = 1
    if keyword.startswith('m163_next_page'):
        is_m163_page = True
        p = keyword.replace('m163_next_page_', '')

    if keyword.startswith('m163_pre_page'):
        is_m163_page = True
        p = keyword.replace('m163_pre_page_', '')

    if is_m163_page:
        is_match, cmd_text = getFaqKw(call.message.text)
        if not is_match:
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id, text="出现错误!")
            return

        data = musicSearch(cmd_text, p, 5)

        dlist = data['result']['songs']
        page_total = math.ceil(data['result']['songCount'] / 5)

        keyboard = []
        for x in dlist:
            keyboard.append([types.InlineKeyboardButton(
                text=x['name'], callback_data='m163:' + str(x['id']))])

        page_nav = []
        if int(p) > 1:
            page_nav.append(types.InlineKeyboardButton(
                text="上一页", callback_data='m163_pre_page_' + str(int(p) - 1)))

        if p < page_total:
            page_nav.append(types.InlineKeyboardButton(
                text="下一页", callback_data='m163_next_page_' + str(int(p) + 1)))

        page_nav.append(types.InlineKeyboardButton(
            text="第" + str(p) + "页,共" + str(page_total) + "页", callback_data='m163_page_total'))

        keyboard.append(page_nav)

        keyboard.append([types.InlineKeyboardButton(
            text="关闭消息", callback_data='m163_search_close')])

        markup = types.InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=call.message.text, reply_markup=markup)


def run(bot, message):
    text_body = message.text

    if isThisCmd('/music', text_body):
        cmd_text = getReadCmd('/music', text_body)
        cmd_text = cmd_text.strip().strip(":")
        if cmd_text == "":
            return bot.send_message(message.chat.id, "搜索内容不能为空, 例如:/music 刀郎")
        return tgSearchMusic(bot, message, cmd_text)

    return bot


if __name__ == '__main__':
    # tgSearchMusic_t("刀郎")
    t = musicSongDataUrl(2063487880)
    print(t['data'][0]['url'])
    print("111")
