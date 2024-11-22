# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import json

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required
from utils.site import sites as MwSites

import core.mw as mw
import thisdb

from .site import blueprint

# 获取网站目录
@blueprint.route('/get_dir_user_ini', endpoint='get_dir_user_ini',methods=['POST'])
@panel_login_required
def get_dir_user_ini():
    site_id = request.form.get('id', '')
    return MwSites.instance().getDirUserIni(site_id)

# 设置防跨站攻击
@blueprint.route('/set_dir_user_ini', endpoint='set_dir_user_ini',methods=['POST'])
@panel_login_required
def set_dir_user_ini():
    path = request.form.get('path', '')
    run_path = request.form.get('run_path', '')
    return MwSites.instance().setDirUserIni(path,run_path)

# 获取子目录绑定
@blueprint.route('/get_dir_binding', endpoint='get_dir_binding',methods=['POST'])
@panel_login_required
def get_dir_binding():
    site_id = request.form.get('id', '')
    return MwSites.instance().getDirBinding(site_id)


# 添加子目录绑定
@blueprint.route('/add_dir_bind', endpoint='add_dir_bind',methods=['POST'])
@panel_login_required
def add_dir_bind():
    site_id = request.form.get('id', '')
    domain = request.form.get('domain', '')
    dir_name = request.form.get('dir_name', '')
    return MwSites.instance().addDirBind(site_id,domain,dir_name)


# 获取目录绑定rewrite
@blueprint.route('/get_dir_bind_rewrite', endpoint='get_dir_bind_rewrite',methods=['POST'])
@panel_login_required
def get_dir_bind_rewrite():
    binding_id = request.form.get('id', '')
    add = request.form.get('add', '')
    return MwSites.instance().getDirBindingRewrite(binding_id,add)


# 获取目录绑定rewrite
@blueprint.route('/del_dir_bind', endpoint='del_dir_bind',methods=['POST'])
@panel_login_required
def del_dir_bind():
    binding_id = request.form.get('id', '')
    return MwSites.instance().delDirBinding(binding_id)


