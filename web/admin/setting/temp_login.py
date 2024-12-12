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

from admin import session
from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.config as utils_config
import thisdb

from .setting import blueprint


@blueprint.route('/get_temp_login', endpoint='get_temp_login', methods=['POST'])
@panel_login_required
def get_temp_login():
    limit = request.form.get('limit', '5').strip()
    p = request.form.get('page', '1').strip()
    tojs = request.form.get('tojs', '').strip()

    info = thisdb.getTempLoginPage(int(p), int(limit))

    data = {}
    data['data'] = info['list']
    data['page'] = mw.getPage({'count':info['count'],'tojs':'setTempAccessReq','p':p,'row':limit})
    return data

@blueprint.route('/set_temp_login', endpoint='set_temp_login', methods=['POST'])
@panel_login_required
def set_temp_login():
    # if 'tmp_login_expire' in session:
    #     return mw.returnData(False, '没有权限')
    

    thisdb.clearTempLogin()

    start_time = int(time.time())
    expire = start_time+3600
    
    rand_str = mw.getRandomString(48)
    token = mw.md5(rand_str)

    r = thisdb.addTempLogin(token, expire)
    if r > 0:
        mw.writeLog('面板设置', '生成临时连接,过期时间:{}'.format(mw.formatDate(times=expire)))
        return {'status': True, 'msg': "临时连接已生成", 'token': token, 'expire': expire}
    return mw.returnData(False, '连接生成失败')

@blueprint.route('/remove_temp_login', endpoint='remove_temp_login', methods=['POST'])
@panel_login_required
def remove_temp_login():
    tl_id = request.form.get('id', '10').strip()
    r = thisdb.deleteTempLoginById(tl_id)
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
        

        



