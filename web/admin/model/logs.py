# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


import json

from admin.model import db, Logs
import core.mw as mw

def add(type, log, uid=1) -> str:
    add_time = mw.formatDate()
    add_logs = Logs(
        uid=uid,
        log=log, 
        type=type,
        add_time=add_time)
    db.session.add(add_logs)
    db.session.commit()
    return True