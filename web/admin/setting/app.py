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

from .setting import blueprint
import thisdb


# 获取APP列表
@blueprint.route('/get_app_list', endpoint='get_app_list', methods=['POST'])
@panel_login_required
def get_app_list():
    limit = request.form.get('limit', '5').strip()
    page = request.form.get('page', '1').strip()
    tojs = request.form.get('tojs', 'getAppList').strip()

    info = thisdb.getAppList(page=int(page),size=int(limit))
    data = {}
    data['data'] = info['list']
    data['page'] = mw.getPage({'count':info['count'],'tojs':tojs,'p':page,'row':limit})
    return data


# 获取APP列表
@blueprint.route('/add_app', endpoint='add_app', methods=['POST'])
@panel_login_required
def add_app():
    app_id = request.form.get('app_id', '').strip()
    app_secret = request.form.get('app_secret', '1').strip()
    limit_addr = request.form.get('limit_addr', '').strip()

    rid = thisdb.addApp(app_id,app_secret,limit_addr)
    if rid > 0:
        return mw.returnData(True, '添加成功!')
    return mw.returnData(False, '添加失败!')


# 获取APP列表
@blueprint.route('/delete_app', endpoint='delete_app', methods=['POST'])
@panel_login_required
def delete_app():
    aid = request.form.get('id', '').strip()
    rid = thisdb.deleteAppById(aid)
    if rid > 0:
        return mw.returnData(True, '删除成功!')
    return mw.returnData(False, '删除失败!')
