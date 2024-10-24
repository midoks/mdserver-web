# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template

from admin.user_login_check import panel_login_required

blueprint = Blueprint('logs', __name__, url_prefix='/logs', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('default/logs.html', data={})


# 日志列表
@blueprint.route('/get_log_list', endpoint='get_log_list', methods=['POST'])
@panel_login_required
def get_log_list():
    return []

# 审计日志列表
@blueprint.route('/get_audit_logs_files', endpoint='get_audit_logs_files', methods=['POST'])
@panel_login_required
def get_audit_logs_files():
    return []