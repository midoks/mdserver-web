# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import time

from admin.model import db, TempLogin

import core.mw as mw

def getTempLoginByToken(token,
) -> None:
    '''
    获取用户信息通过用户名
    '''
    item =  TempLogin.query.filter(TempLogin.token==token).first()
    if item is None:
        return None
    row = {}
    row['id'] = item.id
    row['token'] = item.token
    row['salt'] = item.salt
    row['state'] = item.state
    row['login_time'] = item.login_time
    row['login_addr'] = item.login_addr
    row['logout_time'] = item.logout_time
    row['expire'] = item.expire
    row['add_time'] = item.add_time
    return row

def clearTempLogin()->bool:
    '''
    清空过期数据
    '''
    now_time = int(time.time())
    TempLogin.query.filter(TempLogin.expire<now_time).delete()
    db.session.commit()
    return True