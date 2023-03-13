import sys
import io
import os
import time
import re
import json
import base64
import threading

# import telebot
cmd_list = [
    '/?:',
]


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


def searchFaq(bot, message, cmd_text):
    # print(search_text)
    bot.reply_to(message, cmd_text)
    return True


def run(bot, message):
    text_body = message.text
    if isThisCmd('/?:', text_body):
        cmd_text = getReadCmd('/?:', text_body)
        return searchFaq(bot, message, cmd_text)

    return bot


if __name__ == "__main__":
    print(isThisCmd('/?:', '/?:如何在安装面板'))
    print(getReadCmd('/?:', '/?:如何在安装面板'))
