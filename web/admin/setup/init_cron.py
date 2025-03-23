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

            cron_expression = cron_line.split(maxsplit=5)[0]  # 提取前 5 个字段（* * * * *）
            command = cron_line.split(maxsplit=5)[5]  # 提取命令部分

            # 面板计划任务过滤
            if command.startswith("/www/server/cron"):
                continue


            print(command)

    # cron_list = content.split("\n")
    # print(cron_list)