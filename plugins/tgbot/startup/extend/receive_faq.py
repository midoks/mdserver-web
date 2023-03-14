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
    return_msg = "你正在寻找【" + cmd_text + "】答案:\n"
    return_msg += "此功能还在开发中...请持续关注!\n"
    bot.reply_to(message, return_msg)
    return True


def searchDebugReply(bot, message, cmd_text):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('a')
    itembtn2 = types.KeyboardButton('v')
    itembtn3 = types.KeyboardButton('d')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(chat_id, "Choose one letter:", reply_markup=markup)

    # or add KeyboardButton one row at a time:
    markup = types.ReplyKeyboardMarkup()
    itembtna = types.KeyboardButton('a')
    itembtnv = types.KeyboardButton('v')
    itembtnc = types.KeyboardButton('c')
    itembtnd = types.KeyboardButton('d')
    itembtne = types.KeyboardButton('e')
    markup.row(itembtna, itembtnv)
    markup.row(itembtnc, itembtnd, itembtne)
    bot.send_message(message.chat.id, "Choose one letter:",
                     reply_markup=markup)

    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, message, reply_markup=markup)
    # bot.reply_to(message, "http://baidu.com")
    return True


def searchDebugMsgInline(bot, message, cmd_text):
    button = {
        "如何在安装面板?": {"callback_data": "bbs_id_1"},
        "如何在安装面板2?": {"callback_data": "bbs_id_2"},
        "下一页": {"callback_data": "bbs_pre"},
        "上一页": {"url": "google.com"}
    }

    bot.reply_to(message, "Test",
                 reply_markup=quick_markup(button, row_width=2))
    # bot.send_message(message.chat.id, "Test",reply_markup=quick_markup(button, row_width=2))
    return True


def searchDebug(bot, message, cmd_text):
    searchDebugMsgInline(bot, message, cmd_text)
    return True


def answer_callback_query(bot, call):
    print(call)
    bot.send_message(call.message.chat.id, "Test Callback")
    # bot.answer_callback_query(call.id)


def run(bot, message):
    print(message)
    text_body = message.text
    # print(text_body)
    if isThisCmd('/faq:', text_body):
        cmd_text = getReadCmd('/faq:', text_body)
        return searchFaq(bot, message, cmd_text)

    if isThisCmd('/debug', text_body):
        cmd_text = getReadCmd('/debug', text_body)
        return searchDebug(bot, message, cmd_text)

    if text_body.find('?') > -1 or text_body.find('？') > -1:
        return_msg = "你似乎在寻找【" + text_body + "】答案:\n"
        return_msg += "/faq:开始寻找你的问题\n"
        bot.reply_to(message, return_msg)

    return bot


if __name__ == "__main__":
    print(isThisCmd('/?:', '/?:如何在安装面板'))
    print(getReadCmd('/?:', '/?:如何在安装面板'))
