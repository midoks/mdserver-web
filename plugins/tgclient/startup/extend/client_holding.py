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
from telethon import functions, types
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest
# 指定群ID
chat_id = -1001979545570
filter_user_id = 5568699210

async def run(client):
    while True:
        info = await client.get_dialogs()
        for chat in info:
            print('name:{0} ids:{1} is_user:{2} is_channel:{3} is_group:{4}'.format(
                chat.name, chat.id, chat.is_user, chat.is_channel, chat.is_group))
            if chat.is_group and chat.id != chat_id:
                list_user = []
                async for user in client.iter_participants(chat.id):
                    # print(chat.id, user.id, user.first_name)
                    if filter_user_id != user.id and user.username != None and user.bot == False:
                        # print(user.first_name)
                        list_user.append(user.username)
                        # await client(AddChatUserRequest(
                        #     chat_id=chat_id,  # chat_id
                        #     user_id=user.username,  # 被邀请人id
                        #     fwd_limit=1000  # Allow the user to see the 10 last messages
                        # ))
                # print(list_user)
                try:
                    await client(InviteToChannelRequest(
                        channel=chat_id,  # chat_id
                        users=list_user,  # 被邀请人id
                    ))
                except Exception as e:
                    print(str(e))

                await asyncio.sleep(80000)
            await asyncio.sleep(80000)

if __name__ == "__main__":
    pass
