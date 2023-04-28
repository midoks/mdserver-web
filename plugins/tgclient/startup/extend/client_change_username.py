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


def run(client):
    print(client)
    return ''


if __name__ == "__main__":
    # print(isThisCmd('/?:', '/?:如何在安装面板'))
    # print(getReadCmd('/?:', '/?:如何在安装面板'))
    # print(searchHttpPage('mw'))
    print(getFaqKw('寻找【mw】问题如下:'))
