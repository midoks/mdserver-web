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
from admin import session
from admin.model import db,TempLogin
from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.config as utils_config

from .setting import blueprint


@blueprint.route('/get_temp_login', endpoint='get_temp_login', methods=['POST'])
@panel_login_required
def get_temp_login():
    limit = request.form.get('limit', '5').strip()
    p = request.form.get('page', '1').strip()
    tojs = request.form.get('tojs', '').strip()

    count = TempLogin.query.filter_by().count()
    pagination = TempLogin.query.filter_by().order_by(TempLogin.expire.desc()).paginate(page=int(p), per_page=int(limit))
  
    rows = []
    for item in pagination.items:
        t = {}
        t['id'] = item.id
        t['salt'] = item.salt
        t['state'] = item.state
        t['expire'] = item.expire
        t['login_time'] = item.login_time
        t['login_addr'] = item.login_addr
        t['add_time'] = item.add_time
        rows.append(t)

    data = {}
    data['data'] = rows
    data['page'] = mw.getPage({'count':count,'tojs':'setTempAccessReq','p':p,'row':limit})
    return data

@blueprint.route('/set_temp_login', endpoint='set_temp_login', methods=['POST'])
@panel_login_required
def set_temp_login():
    # if 'tmp_login_expire' in session:
    #     return mw.returnData(False, '没有权限')
    start_time = int(time.time())
    model.clearTempLogin()


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

    if r is None:
        mw.writeLog('面板设置', '生成临时连接,过期时间:{}'.format(mw.formatDate(times=expire)))
        return {'status': True, 'msg': "临时连接已生成", 'token': make_token, 'expire': expire}
    return mw.returnData(False, '连接生成失败')

@blueprint.route('/remove_temp_login', endpoint='remove_temp_login', methods=['POST'])
@panel_login_required
def remove_temp_login():
    tl_id = request.form.get('id', '10').strip()

    r = TempLogin.query.filter(TempLogin.id == tl_id).delete()
    db.session.commit()
    if r > 0:
        mw.writeLog('面板设置', '删除临时登录连接')
        return mw.returnData(True, '删除成功')
    return mw.returnData(False, '删除失败')


@blueprint.route('/get_temp_login_logs', endpoint='get_temp_login_logs', methods=['POST'])
@panel_login_required
def get_temp_login_logs():
    if 'tmp_login_expire' in session:
        return mw.returnData(False, '没有权限')
    return mw.returnData(False, 'ok', [])
        

        



