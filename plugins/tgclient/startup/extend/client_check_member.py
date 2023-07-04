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
chat_id_list = [-1001979545570]
# 别人群ID[有API调用限制]
chat_id_list_other = [-1001578009023, -1001771526434]

async def writeLog(log_str):
    if __name__ == "__main__":
        print(log_str)

    now = mw.getDateFromNow()
    log_file = mw.getServerDir() + '/tgclient/task.log'
    mw.writeFileLog(now + ':' + log_str, log_file, limit_size=5 * 1024)
    return True

async def run(client):
    for chat_id in chat_id_list:
        try:
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
        except Exception as e:
            print(str(e))
            writeLog(str(e))

    for chat_id in chat_id_list_other:
        try:
            async for user in client.iter_participants(chat_id):
                if user.deleted:
                    msg = await client.kick_participant(chat_id, user)
        except Exception as e:
            print(str(e))
            writeLog(str(e))

    await asyncio.sleep(300)


if __name__ == "__main__":
    pass
