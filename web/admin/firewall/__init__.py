# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

from utils.firewall import Firewall as MwFirewall

import core.mw as mw
import thisdb

blueprint = Blueprint('firewall', __name__, url_prefix='/firewall', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    name = thisdb.getOption('template', default='default')
    return render_template('%s/firewall.html' % name)


# 防火墙列表
@blueprint.route('/get_list', endpoint='get_list', methods=['POST'])
@panel_login_required
def get_list():
    p = request.form.get('p', '1').strip()
    limit = request.form.get('limit', '10').strip()
    return MwFirewall.instance().getList(p,limit)

# 获取站点日志目录
@blueprint.route('/get_www_path', endpoint='get_www_path', methods=['POST'])
@panel_login_required
def get_www_path():
    path = mw.getLogsDir()
    return {'path': path}

# 获取ssh信息
@blueprint.route('/get_ssh_info', endpoint='get_ssh_info', methods=['POST'])
@panel_login_required
def get_ssh_info():
    return MwFirewall.instance().getSshInfo()


# 切换ping开关
@blueprint.route('/set_ping', endpoint='set_ping', methods=['POST'])
@panel_login_required
def set_ping():
    status = request.form.get('status')
    return MwFirewall.instance().setPing(status)

# 修改ssh端口
@blueprint.route('/set_ssh_port', endpoint='set_ssh_port', methods=['POST'])
@panel_login_required
def set_ssh_port():
    port = request.form.get('port', '1').strip()
    return MwFirewall.instance().setSshPort(port)

# 添加放行端口
@blueprint.route('/add_accept_port', endpoint='add_accept_port', methods=['POST'])
@panel_login_required
def add_accept_port():
    port = request.form.get('port', '').strip()
    ps = request.form.get('ps', '').strip()
    protocol = request.form.get('protocol', '').strip()
    stype = request.form.get('type', '').strip()

    return MwFirewall.instance().addAcceptPort(port, ps, stype, protocol=protocol)

# 删除放行端口
@blueprint.route('/del_accept_port', endpoint='del_accept_port', methods=['POST'])
@panel_login_required
def del_accept_port():
    port = request.form.get('port', '').strip()
    firewall_id = request.form.get('id', '').strip()
    protocol = request.form.get('protocol', '').strip()
    return MwFirewall.instance().delAcceptPort(firewall_id, port, protocol=protocol)


# 设置防火墙状态
@blueprint.route('/set_fw', endpoint='set_fw', methods=['POST'])
@panel_login_required
def set_fw():
    if mw.isAppleSystem():
        return mw.returnData(True, '开发机不能设置!')
    status = request.form.get('status', '1')
    return MwFirewall.instance().setFw(status)

@blueprint.route('/set_ssh_pass_status', endpoint='set_ssh_pass_status', methods=['POST'])
@panel_login_required
def set_ssh_pass_status():
    if mw.isAppleSystem():
        return mw.returnData(True, '开发机不能设置!')
    status = request.form.get('status', '1')
    return MwFirewall.instance().setSshPassStatus(status)

@blueprint.route('/set_ssh_pubkey_status', endpoint='set_ssh_pubkey_status', methods=['POST'])
@panel_login_required
def set_ssh_pubkey_status():
    if mw.isAppleSystem():
        return mw.returnData(True, '开发机不能设置!')
    status = request.form.get('status', '1')
    return MwFirewall.instance().setSshPubkeyStatus(status)







