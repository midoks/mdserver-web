# coding:utf-8

# func: 在其他发送推送AD
# url: https://docs.telethon.dev/en/stable/modules/client.html
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


msg_ad = "本人软件推广(10s)\n\n"
msg_ad += "开源Linux面板【mdserver-web】,站长必备,无毒,源码为证。\n"
msg_ad += "不收费,全靠TG乞讨! \n"
msg_ad += "看个人简介,加入群聊,一起进步!\n"
# msg_ad += "https://github.com/midoks/mdserver-web \n"
# msg_ad += "\n"
# msg_ad += "加入群聊,一起进步! \n"
# msg_ad += "https://t.me/mdserver_web \n"
# msg_ad += "不收费,无毒。源码为证。全靠TG乞讨!😭\n\n"
# msg_ad += "捐赠地址 USDT（TRC20）\n"
# msg_ad += "TVbNgrpeGBGZVm5gTLa21ADP7RpnPFhjya\n"
# msg_ad += "日行一善，以后必定大富大贵\n"


async def writeLog(log_str):
    if __name__ == "__main__":
        print(log_str)

    now = mw.getDateFromNow()
    log_file = mw.getServerDir() + '/tgclient/task.log'
    mw.writeFileLog(now + ':' + log_str, log_file, limit_size=5 * 1024)
    return True

async def send_msg(client, chat_id, tag='ad', trigger_time=600):
    # 信号只在一个周期内执行一次|start
    lock_file = mw.getServerDir() + '/tgclient/lock.json'
    if not os.path.exists(lock_file):
        mw.writeFile(lock_file, '{}')

    lock_data = json.loads(mw.readFile(lock_file))
    if tag in lock_data:
        diff_time = time.time() - lock_data[tag]['do_time']
        if diff_time >= trigger_time:
            lock_data[tag]['do_time'] = time.time()
        else:
            return False, 0, 0
    else:
        lock_data[tag] = {'do_time': time.time()}
    mw.writeFile(lock_file, json.dumps(lock_data))
    # 信号只在一个周期内执行一次|end

    msg = await client.send_message(chat_id, msg_ad)
    await asyncio.sleep(10)
    await client.delete_messages(chat_id, msg)
    await asyncio.sleep(3)

async def run(client):
    client.parse_mode = 'html'
    # for chat_id in chat_id_list:
    #     await send_msg(client, chat_id)
    #     await asyncio.sleep(30)

    info = await client.get_dialogs()
    for chat in info:
        if chat.is_group and not chat.id in filter_g_id:
            chat_id = str(chat.id)
            if chat_id[0:4] != '-100':
                continue

            # print(chat)
            await writeLog('name:{0} id:{1} is_user:{2} is_channel:{3} is_group:{4}'.format(
                chat.name, chat.id, chat.is_user, chat.is_channel, chat.is_group))
            try:
                await send_msg(client, chat.id, 'ad_' + str(chat.id))
            except Exception as e:
                await writeLog(str(chat))
                await writeLog(str(e))


if __name__ == "__main__":
    pass
