# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import core.mw as mw
from utils.crontab import crontab
from croniter import croniter
from datetime import datetime
import thisdb

def cron_todb(data):
    # print("------")
    rdata = {}
    if data[3] == "*" and data[2] != "*" :
        rdata['type'] = 'month'
    elif data[3] == "*" and data[4] != "*" :
        rdata['type'] = 'week'
    elif data[3] == "*" and data[4] == "*" and data[2] == "*" :
        rdata['type'] = 'day'
    elif data[1].find("/") > -1 :
        rdata['type'] = 'hour-n'
    elif data[0].find("/") > -1 :
        rdata['type'] = 'minute-n'

    # print(rdata)
    # print(data)
    return rdata
    # print("------")

def init_acme_cron():
    name = "[勿删]ACME定时强制更新"
    res = mw.M("crontab").field("id, name").where("name=?", (name,)).find()
    if res:
        return True

    cmd = "/root/.acme.sh/acme.sh --cron --force --standalone"
    params = {
        'name': name,
        'type': 'day-n',
        'week': "",
        'where1': "7",
        'hour': 4,
        'minute': 15,
        'save': "",
        'backup_to': "",
        'stype': "toShell",
        'sname': '',
        'sbody': cmd,
        'url_address': '',
        'attr':'',
    }

    crontab.instance().add(params)
    return True

def init_auto_update():
    name = "[可删]面板自动更新"
    res = mw.M("crontab").field("id, name").where("name=?", (name,)).find()
    if res:
        return True

    cmd = "mw update"
    params = {
        'name': name,
        'type': 'month',
        'week': "",
        'where1': "1",
        'hour': 4,
        'minute': 15,
        'save': "",
        'backup_to': "",
        'stype': "toShell",
        'sname': '',
        'sbody': cmd,
        'url_address': '',
        'attr':'',
    }

    crontab.instance().add(params)
    return True

# 识别linux计划任务
def init_cron():
    file = ''
    cron_file = [
        '/var/spool/cron/crontabs/root',
        '/var/spool/cron/root',
    ]
    for i in cron_file:
        if os.path.exists(i):
            file = i

    if file == "":
        return True

    with open(file) as f:
        for line in f.readlines():
            cron_line = line.strip()
            if cron_line.startswith("#"):
                continue

            cron_expression = cron_line.split(maxsplit=5)  # 提取前 5 个字段（* * * * *）
            command = cron_line.split(maxsplit=5)[5]  # 提取命令部分

            # 面板计划任务过滤
            if command.startswith("/www/server/cron"):
                continue

            if command.startswith("\"/root/.acme.sh\""):
                # print(cron_expression, command)
                info = cron_todb(cron_expression)

                # print(info)

                # add_dbdata = {}
                # add_dbdata['name'] = "ACME"
                # add_dbdata['type'] = data['type']
                # add_dbdata['where1'] = data['where1']
                # add_dbdata['where_hour'] = data['hour']
                # add_dbdata['where_minute'] = data['minute']
                # add_dbdata['save'] = ""
                # add_dbdata['backup_to'] = ""
                # add_dbdata['sname'] = ""
                # add_dbdata['sbody'] = data['sbody']
                # add_dbdata['stype'] = "toShell"
                # add_dbdata['echo'] = command
                # add_dbdata['url_address'] = ''

                # thisdb.addCrontab(add_dbdata)

            # print(command)

    # cron_list = content.split("\n")
    # print(cron_list)