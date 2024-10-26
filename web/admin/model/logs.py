# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


import json
import time

from admin.model import db, Logs

def formatDate(format="%Y-%m-%d %H:%M:%S", times=None):
    # 格式化指定时间戳
    if not times:
        times = int(time.time())
    time_local = time.localtime(times)
    return time.strftime(format, time_local)

def addLog(type, log,
    uid: int | None = 1
) -> str:
    '''
    添加日志
    :type -> str 类型 (必填)
    :log -> str 日志内容 (必填)
    :uid -> int 用户ID
    '''
    add_time = formatDate()
    add_logs = Logs(
        uid=uid,
        log=log, 
        type=type,
        add_time=add_time)
    db.session.add(add_logs)
    db.session.commit()
    return True