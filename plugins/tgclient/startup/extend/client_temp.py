# coding:utf-8

# func: 临时测试

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
from telethon import functions, types
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest
# 指定群ID
chat_id = -1001979545570
filter_user_id = 5568699210
filter_g_id = [-1001771526434]


async def run(client):

    my_channel = await client.get_entity(PeerChannel(-1001173826177))
    print(my_channel)

    for i in range(9999999999):
        try:
            v = -1001000000000 - i
            my_channel = await client.get_entity(PeerChannel(v))
            print(my_channel)
        except Exception as e:
            pass

    # -1001809140739
    # -1001800000000
    # -1000000000001

    info = await client.get_dialogs()
    for chat in info:
        if not chat.is_group and chat.is_channel:
            print('name:{0} id:{1} is_user:{2} is_channel:{3} is_group:{4}'.format(
                chat.name, chat.id, chat.is_user, chat.is_channel, chat.is_group))
    await asyncio.sleep(10)


if __name__ == "__main__":
    pass
