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
    data = httpPost('http://music.163.com/api/cloudsearch/pc', {
        's': kw,
        'type': '1',
        'total': 'true',
        'limit': page_size,
        'offset': 0,
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


def tgSearchMusic(bot, message, cmd_text):
    data = musicSearch(cmd_text, 1, 5)
    print(data)


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
    # musicSearch("刀郎")
    t = musicSongDataUrl(2063487880)
    print(t['data'][0]['url'])
    print("111")
