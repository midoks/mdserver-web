# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import re
import json
import os
import time

from flask import Blueprint, render_template
from flask import request

from admin import model
from admin.model import db,TempLogin
from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.config as utils_config

from .main import blueprint


@blueprint.route('/set_temp_login', endpoint='set_temp_login', methods=['POST'])
@panel_login_required
def set_temp_login():
    # if 'tmp_login_expire' in session:
    #     return mw.returnData(False, '没有权限')
    start_time = int(time.time())
    # mw.M('temp_login').where(
    #     'state=? and expire>?', (0, start_time)).delete()


    token = mw.getRandomString(48)
    salt = mw.getRandomString(12)

    expire=start_time+3600
    make_token = mw.md5(token + salt)
    add_tl = TempLogin(
        token=make_token,
        salt=salt,
        state=0,
        login_time=0,
        login_addr='',
        expire=expire,
        add_time=start_time)
    r = db.session.add(add_tl)
    db.session.commit()


    # if not mw.M('temp_login').count():
    #     pdata['id'] = 101

    # if mw.M('temp_login').insert(pdata):
    #     mw.writeLog('面板设置', '生成临时连接,过期时间:{}'.format(mw.formatDate(times=pdata['expire'])))
    #     return mw.getJson({'status': True, 'msg': "临时连接已生成", 'token': token, 'expire': pdata['expire']})
    return mw.returnData(False, '连接生成失败')



