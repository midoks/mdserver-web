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

from utils.setting import setting as MwSetting

from .setting import blueprint
import thisdb

# 添加面板书签
@blueprint.route('/add_panel_info', endpoint='add_panel_info', methods=['POST'])
@panel_login_required
def add_panel_info():
    title = request.form.get('title', '')
    url = request.form.get('url', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    # 校验是还是重复
    isAdd = mw.M('panel').where('title=? OR url=?', (title, url)).count()
    if isAdd:
        return mw.returnData(False, '备注或面板地址重复!')
    isRe = mw.M('panel').add('title,url,username,password,click,add_time',
            (title, url, username, password, 0, int(time.time())))
    if isRe:
        return mw.returnData(True, '添加成功!')
    return mw.returnData(False, '添加失败!')

# 取面板书签列表
@blueprint.route('/get_panel_list', endpoint='get_panel_list', methods=['GET','POST'])
@panel_login_required
def get_panel_list():
    data = mw.M('panel').field('id,title,url,username,password,click,add_time').order('click desc').select()
    return mw.returnData(True, 'ok!', data)


# 删除面板书签
@blueprint.route('/del_panel_info', endpoint='del_panel_info', methods=['GET','POST'])
@panel_login_required
def del_panel_info():
    panel_id = request.form.get('id', '')
    isExists = mw.M('panel').where('id=?', (panel_id,)).count()
    if not isExists:
        return mw.returnData(False, '指定面板资料不存在!')
    mw.M('panel').where('id=?', (panel_id,)).delete()
    return mw.returnData(True, '删除成功!')


# 设置面板域名
@blueprint.route('/set_panel_info', endpoint='set_panel_info', methods=['POST'])
@panel_login_required
def set_panel_info():
    title = request.form.get('title', '')
    url = request.form.get('url', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    panel_id = request.form.get('id', '')
    # 校验是还是重复
    isSave = mw.M('panel').where('(title=? OR url=?) AND id!=?', (title, url, panel_id)).count()
    if isSave:
        return mw.returnData(False, '备注或面板地址重复!')

    # 更新到数据库
    isRe = mw.M('panel').where('id=?', (panel_id,)).save('title,url,username,password', (title, url, username, password))
    if isRe:
        return mw.returnData(True, '修改成功!')
    return mw.returnData(False, '修改失败!')

