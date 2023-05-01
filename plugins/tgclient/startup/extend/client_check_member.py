# coding:utf-8

# func: 自动检测已经注销群成员

import sys
import io
import os
import time
import re
import json
import base64
import threading
import asyncio

sys.path.append(os.getcwd() + "/class/core")
import mw

import telebot
from telebot import types
from telebot.util import quick_markup


# 指定群ID
chat_id_list = [-1001578009023, -953760154]

async def run(client):
    while True:
        for chat_id in chat_id_list:
            s = await client.send_message(chat_id, '开始自动检测已经注销群成员...')
            count = 0
            async for user in client.iter_participants(chat_id):
                if user.deleted:
                    count += 1
                    msg = await client.kick_participant(chat_id, user)

            await client.edit_message(chat_id, s.id, '已经检测到有(%d)个账户已失效' % (count))
            await asyncio.sleep(3)
            await client.edit_message(chat_id, s.id, '自动检测已经注销群成员完毕!!!')
            await asyncio.sleep(3)
            await client.delete_messages(chat_id, s)
            await asyncio.sleep(300)


if __name__ == "__main__":
    pass
