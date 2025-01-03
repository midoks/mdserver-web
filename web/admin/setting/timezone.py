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

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.config as utils_config

from .setting import blueprint

# 时区相关
@blueprint.route('/get_timezone_list', endpoint='get_timezone_list', methods=['POST'])
@panel_login_required
def get_timezone_list():
    import pytz
    # 获取时区列表
    # pytz.all_timezones | 所有
    # pytz.common_timezones
    return mw.returnData(True, 'ok', pytz.all_timezones)

@blueprint.route('/sync_date', endpoint='sync_date', methods=['POST'])
@panel_login_required
def sync_date():
    if mw.isAppleSystem():
        return mw.returnData(True, '开发系统不必同步时间!')
    data = mw.execShell('ntpdate -s time.nist.gov')
    if data[0] == '':
        return mw.returnData(True, '同步成功!')
    return mw.returnData(False, '同步失败:' + data[0])

@blueprint.route('/set_timezone', endpoint='set_timezone', methods=['POST'])
@panel_login_required
def set_timezone():
    # 设置时区列表
    timezone = request.form.get('timezone', '').strip()
    cmd = 'timedatectl set-timezone "'+timezone+'"'
    mw.execShell(cmd)
    return mw.returnData(True, '设置成功!')
        

        
        


 