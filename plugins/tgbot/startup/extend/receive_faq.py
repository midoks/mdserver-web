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


def searchFaq(bot, message):
    # print(search_text)
    bot.reply_to(message, message.chat.id)
    return True


def run(bot, message):
    text_body = message.text
    for cmd in cmd_list:
        if isThisCmd(cmd, text_body):
            return searchFaq(bot, message)

    return bot


if __name__ == "__main__":
    print(isThisCmd('/?:', '/?:如何在安装面板'))
