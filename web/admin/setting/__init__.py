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

from admin import model
from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.config as utils_config

# 默认页面
blueprint = Blueprint('setting', __name__, url_prefix='/setting', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    return render_template('default/setting.html')

@blueprint.route('/get_panel_list', endpoint='get_panel_list', methods=['POST'])
@panel_login_required
def get_panel_list():
    return []


# 设置面板名称
@blueprint.route('/set_webname', endpoint='set_webname', methods=['POST'])
@panel_login_required
def set_webname():
    webname = request.form.get('webname', '')
    src_webname = model.getOption('title')
    if webname != src_webname:
        model.setOption('title', webname)
    return mw.returnData(True, '面板别名保存成功!')

# 设置服务器IP
@blueprint.route('/set_ip', endpoint='set_ip', methods=['POST'])
@panel_login_required
def set_ip():
    host_ip = request.form.get('host_ip', '')
    src_host_ip = model.getOption('server_ip')
    if host_ip != src_host_ip:
        model.setOption('server_ip', host_ip)
    return mw.returnData(True, 'IP保存成功!')

# 默认备份目录
@blueprint.route('/set_backup_dir', endpoint='set_backup_dir', methods=['POST'])
@panel_login_required
def set_backup_dir():
    backup_path = request.form.get('backup_path', '')
    src_backup_path = model.getOption('backup_path')
    if backup_path != src_backup_path:
        model.setOption('backup_path', backup_path)
    return mw.returnData(True, '修改默认备份目录成功!')

# 默认站点目录
@blueprint.route('/set_www_dir', endpoint='set_www_dir', methods=['POST'])
@panel_login_required
def set_www_dir():
    sites_path = request.form.get('sites_path', '')
    src_sites_path = model.getOption('sites_path')
    if sites_path != src_sites_path:
        model.setOption('sites_path', sites_path)
    return mw.returnData(True, '修改默认建站目录成功!')


# 设置安全入口
@blueprint.route('/set_admin_path', endpoint='set_admin_path', methods=['POST'])
@panel_login_required
def set_admin_path():
    admin_path = request.form.get('admin_path', '')
    admin_path_sensitive = [
        '/', '/close', '/login',
        '/do_login', '/site', '/sites',
        '/download_file', '/control', '/crontab',
        '/firewall', '/files', '/config', '/setting','/monitor'
        '/soft', '/system', '/code',
        '/ssl', '/plugins', '/hook'
    ]

    if admin_path == '':
        admin_path = '/'

    if admin_path != '/':
        if len(admin_path) < 6:
            return mw.returnData(False, '安全入口地址长度不能小于6位!')
        if admin_path in admin_path_sensitive:
            return mw.returnData(False, '该入口已被面板占用,请使用其它入口!')
        if not re.match(r"^/[\w]+$", admin_path):
            return mw.returnData(False, '入口地址格式不正确,示例: /mw_rand')
    
    src_admin_path = model.getOption('admin_path')
    if admin_path != src_admin_path:
        model.setOption('admin_path', admin_path[1:])
    return mw.returnData(True, '修改成功!')



# 设置BasicAuth认证
@blueprint.route('/set_basic_auth', endpoint='set_basic_auth', methods=['POST'])
@panel_login_required
def set_basic_auth():
    basic_user = request.form.get('basic_user', '').strip()
    basic_pwd = request.form.get('basic_pwd', '').strip()
    basic_open = request.form.get('is_open', '').strip()
    
    __file = mw.getCommonFile()
    path = __file['basic_auth']

    is_open = True
    if basic_open == 'false':
        is_open = False

    if basic_open == 'false':
        model.setOption('basic_auth', json.dumps({'open':False}))
        mw.writeLog('面板设置', '设置BasicAuth状态为: %s' % is_open)
        return mw.returnData(True, '删除BasicAuth成功!')

    if basic_user == '' or basic_pwd == '':
        return mw.returnData(False, '用户和密码不能为空!')

    salt = mw.getRandomString(6)
    data = {}
    data['salt'] = salt
    data['basic_user'] = mw.md5(basic_user + salt)
    data['basic_pwd'] = mw.md5(basic_pwd + salt)
    data['open'] = is_open

    model.setOption('basic_auth', json.dumps(data))
    mw.writeLog('面板设置', '设置BasicAuth状态为: %s' % is_open)
    return mw.returnData(True, '设置成功!')


# 默认站点目录
@blueprint.route('/set_status_code', endpoint='set_status_code', methods=['POST'])
@panel_login_required
def set_status_code():
    status_code = request.form.get('status_code', '').strip()
    if re.match(r"^\d+$", status_code):
        status_code = int(status_code)
        if status_code != 0:
            if status_code < 100 or status_code > 999:
                return mw.returnData(False, '状态码范围错误!!')
    else:
        return mw.returnData(False, '状态码范围错误!')

    info = utils_config.getUnauthStatus(code=str(status_code))
    model.setOption('unauthorized_status', str(status_code))
    mw.writeLog('面板设置', '将未授权响应状态码设置为:{0}:{1}'.format(status_code,info['text']))
    return mw.returnData(True, '设置成功!')





 