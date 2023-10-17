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


def init(bot):
    bot.delete_my_commands(scope=None, language_code=None)
    bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("start", "查看帮助信息"),
            telebot.types.BotCommand("faq", "BBS帮助"),
            telebot.types.BotCommand("music", "搜索网易音乐"),
        ],
    )
