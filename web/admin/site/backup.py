# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

from utils.plugin import plugin as MwPlugin
from utils.site import sites as MwSites

import core.mw as mw
import thisdb

from .site import blueprint

# 获取备份列表
@blueprint.route('/get_backup', endpoint='get_backup',methods=['POST'])
@panel_login_required
def get_backup():
    limit = request.form.get('limit', '')
    page = request.form.get('p', '')
    site_id = request.form.get('search', '')
    return MwSites.instance().getBackup(site_id,page=page,size=limit)

# 设置备份
@blueprint.route('/to_backup', endpoint='to_backup',methods=['POST'])
@panel_login_required
def to_backup():
    site_id = request.form.get('id', '')
    return MwSites.instance().toBackup(site_id)

# 删除备份
@blueprint.route('/del_backup', endpoint='del_backup',methods=['POST'])
@panel_login_required
def del_backup():
    site_id = request.form.get('id', '')
    return MwSites.instance().delBackup(site_id)







