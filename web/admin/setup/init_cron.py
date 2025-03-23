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

    # content = mw.execShell("crontab -l")
    with open(file) as f:
        for line in f.readlines():
            cron_line = line.strip()
            if cron_line.startswith("#"):
                continue
            print(cron_line)

    # cron_list = content.split("\n")
    # print(cron_list)