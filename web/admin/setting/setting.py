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
import thisdb
import utils.config as utils_config


# 默认页面
blueprint = Blueprint('setting', __name__, url_prefix='/setting', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    name = thisdb.getOption('template', default='default')
    return render_template('%s/setting.html' % name)

# 设置面板名称
@blueprint.route('/set_webname', endpoint='set_webname', methods=['POST'])
@panel_login_required
def set_webname():
    webname = request.form.get('webname', '')
    src_webname = thisdb.getOption('title')
    if webname != src_webname:
        thisdb.setOption('title', webname)
    return mw.returnData(True, '面板别名保存成功!')

# 设置服务器IP
@blueprint.route('/set_ip', endpoint='set_ip', methods=['POST'])
@panel_login_required
def set_ip():
    host_ip = request.form.get('host_ip', '')
    src_host_ip = thisdb.getOption('server_ip')
    if host_ip != src_host_ip:
        thisdb.setOption('server_ip', host_ip)
    return mw.returnData(True, 'IP保存成功!')

# 默认备份目录
@blueprint.route('/set_backup_dir', endpoint='set_backup_dir', methods=['POST'])
@panel_login_required
def set_backup_dir():
    backup_path = request.form.get('backup_path', '')
    src_backup_path = thisdb.getOption('backup_path')
    if backup_path != src_backup_path:
        thisdb.setOption('backup_path', backup_path)
    return mw.returnData(True, '修改默认备份目录成功!')

# 默认站点目录
@blueprint.route('/set_www_dir', endpoint='set_www_dir', methods=['POST'])
@panel_login_required
def set_www_dir():
    sites_path = request.form.get('sites_path', '')
    src_sites_path = thisdb.getOption('site_path')
    if sites_path != src_sites_path:
        thisdb.setOption('site_path', sites_path)
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
    
    src_admin_path = thisdb.getOption('admin_path')
    if admin_path != src_admin_path:
        thisdb.setOption('admin_path', admin_path[1:])
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
        thisdb.setOption('basic_auth', json.dumps({'open':False}))
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

    thisdb.setOption('basic_auth', json.dumps(data))
    mw.writeLog('面板设置', '设置BasicAuth状态为: %s' % is_open)
    return mw.returnData(True, '设置成功!')


# 设置面板未登录状态
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
    thisdb.setOption('unauthorized_status', str(status_code))
    mw.writeLog('面板设置', '将未授权响应状态码设置为:{0}:{1}'.format(status_code,info['text']))
    return mw.returnData(True, '设置成功!')

# 设置面板调式模式
@blueprint.route('/open_debug', endpoint='open_debug', methods=['POST'])
@panel_login_required
def open_debug():
    debug = thisdb.getOption('debug',default='close')
    if debug == 'open':
        thisdb.setOption('debug','close')
        return mw.returnData(True, '开发模式关闭!')
    thisdb.setOption('debug','open')
    return mw.returnData(True, '开发模式开启!')


# 设置面板开关
@blueprint.route('/close_panel', endpoint='close_panel', methods=['POST'])
@panel_login_required
def close_panel():
    admin_close = thisdb.getOption('admin_close',default='no')
    if admin_close == 'no':
        thisdb.setOption('admin_close','yes')
        return mw.returnData(True, '关闭面板成功!')
    thisdb.setOption('admin_close','no')
    return mw.returnData(True, '开启面板成功!')

# 设置IPV6状态
@blueprint.route('/set_ipv6_status', endpoint='set_ipv6_status', methods=['POST'])
@panel_login_required
def set_ipv6_status():
    __file = mw.getCommonFile()
    ipv6_file = __file['ipv6']
    if os.path.exists(ipv6_file):
        os.remove(ipv6_file)
        mw.writeLog('面板设置', '关闭面板IPv6兼容!')
        mw.returnData('面板设置', '关闭面板IPv6兼容!')
    else:
        mw.writeFile(ipv6_file, 'True')
        mw.writeLog('面板设置', '开启面板IPv6兼容!')
    mw.restartMw()
    return mw.returnData(True, '设置成功!')

# 设置面板用户
@blueprint.route('/set_name', endpoint='set_name', methods=['POST'])
@panel_login_required
def set_name():
    name1 = request.form.get('name1', '')
    name2 = request.form.get('name2', '')
    if name1 != name2:
        return mw.returnData(False, '两次输入的用户名不一致，请重新输入!')
    if len(name1) < 3:
        return mw.returnData(False, '用户名长度不能少于3位')
    thisdb.setUserByName(session['username'], name1)
    session['username'] = name1
    return mw.returnData(True, '用户修改成功!')

# 设置面板密码
@blueprint.route('/set_password', endpoint='set_password', methods=['POST'])
@panel_login_required
def set_password():
    password1 = request.form.get('password1', '')
    password2 = request.form.get('password2', '')
    if password1 != password2:
        return mw.returnData(False, '两次输入的密码不一致，请重新输入!')
    if len(password1) < 5:
        return mw.returnData(False, '用户密码不能小于5位!')

    thisdb.setUserPwdByName(session['username'], password1)
    return mw.returnData(True, '密码修改成功!')

# 设置面板端口
@blueprint.route('/set_port', endpoint='set_port', methods=['POST'])
@panel_login_required
def set_port():
    port = request.form.get('port', '')
    if port != mw.getHostPort():
        from utils.firewall import Firewall as MwFirewall

        sysCfgDir = mw.systemdCfgDir()
        if os.path.exists(sysCfgDir + "/firewalld.service"):
            if not MwFirewall.instance().getFwStatus():
                return mw.returnData(False, 'firewalld必须先启动!')

        mw.setHostPort(port)
        msg = mw.getInfo('放行端口[{1}]成功', (port,))
        mw.writeLog("防火墙管理", msg)

        MwFirewall.instance().addAcceptPort(port, 'PANEL端口-配置修改', 'port')
        mw.restartMw()

    return mw.returnData(True, '端口保存成功!')
 