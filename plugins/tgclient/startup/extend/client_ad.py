# coding:utf-8

# func: 在其他发送推送AD

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
chat_id_list = [-1001578009023]
filter_g_id = [-1001771526434]


async def run(client):
    while True:
        for chat_id in chat_id_list:
            s = await client.send_message(chat_id, '推送消息测试')
            await asyncio.sleep(30)
            await client.delete_messages(chat_id, s)
        await asyncio.sleep(3)
        # info = await client.get_dialogs()
        # for chat in info:
        #     is_sleep = True
        #     print('name:{0} id:{1} is_user:{2} is_channel:{3} is_group:{4}'.format(
        #         chat.name, chat.id, chat.is_user, chat.is_channel, chat.is_group))
        #     if chat.is_group and chat.id != chat_id:
        #         list_user = []
        #         async for user in client.iter_participants(chat.id):
        #             if chat.id in filter_g_id:
        #                 is_sleep = False
        #                 continue

        #             if filter_user_id != user.id and user.username != None and user.bot == False:
        #                 list_user.append(user.username)
        #         print(list_user)
        #         try:
        #             await client(InviteToChannelRequest(
        #                 channel=chat_id,  # chat_id
        #                 users=list_user,  # 被邀请人id
        #             ))
        #         except Exception as e:
        #             print(str(e))
        #         if is_sleep:
        #             await asyncio.sleep(90000)

if __name__ == "__main__":
    pass
