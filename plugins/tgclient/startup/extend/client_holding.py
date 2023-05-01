# coding:utf-8

# func: 自动邀请群成员

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

from telethon import utils


# 指定群ID
chat_id = -953760154

async def run(client):
    info = await client.get_dialogs()
    for chat in info:
        if chat.is_group:
            print('name:{0} ids:{1} is_user:{2} is_channel{3} is_group:{4}'.format(
                chat.name, chat.id, chat.is_user, chat.is_channel, chat.is_group))


if __name__ == "__main__":
    pass
