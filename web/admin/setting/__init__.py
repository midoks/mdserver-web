# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import re

from flask import Blueprint, render_template
from flask import request

from admin import model
import core.mw as mw

# 默认页面
blueprint = Blueprint('setting', __name__, url_prefix='/setting', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('default/setting.html')



@blueprint.route('/get_panel_list', endpoint='get_panel_list', methods=['POST'])
def get_panel_list():
    return []


# 设置面板名称
@blueprint.route('/set_webname', endpoint='set_webname', methods=['POST'])
def set_webname():
    webname = request.form.get('webname', '')
    src_webname = model.getOption('title')
    if webname != src_webname:
        model.setOption('title', webname)
    return mw.returnData(True, '面板别名保存成功!')

# 设置服务器IP
@blueprint.route('/set_ip', endpoint='set_ip', methods=['POST'])
def set_ip():
    host_ip = request.form.get('host_ip', '')
    src_host_ip = model.getOption('server_ip')
    if host_ip != src_host_ip:
        model.setOption('server_ip', host_ip)
    return mw.returnData(True, 'IP保存成功!')

# 设置安全入口
@blueprint.route('/set_admin_path', endpoint='set_admin_path', methods=['POST'])
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




 