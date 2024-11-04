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
    field = 'id,addtime,expire,login_time,login_addr,state,add_time'
    data = mw.M('temp_login').where('token=?', (token,)).field(field).order('id asc').select()
    return data

def clearTempLogin()->bool:
    '''
    清空过期数据
    '''

    now_time = int(time.time())
    mw.M('temp_login').where('expire<?', (now_time)).delete()
    return True