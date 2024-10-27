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
from admin.model import db, Logs

import core.mw as mw
import utils.adult_log as adult_log

# 日志页面
blueprint = Blueprint('logs', __name__, url_prefix='/logs', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('default/logs.html')


# 日志列表
@blueprint.route('/get_log_list', endpoint='get_log_list', methods=['POST'])
@panel_login_required
def get_log_list():
    p = request.form.get('p', '1').strip()
    size = request.form.get('limit', '10').strip()
    search = request.form.get('search', '').strip()

    count = Logs.query.filter_by().count()
    if search != '':
        pagination = Logs.query.filter_by(Logs.type.like(search) or Logs.log.like(search)).paginate(page=int(p), per_page=int(size))
    else:
        pagination = Logs.query.filter_by().order_by(Logs.id.desc()).paginate(page=int(p), per_page=int(size))
  
    rows = []
    for item in pagination.items:
        t = {}
        t['id'] = item.id
        t['type'] = item.type
        t['log'] = item.log
        t['uid'] = item.uid
        t['add_time'] = item.add_time
        rows.append(t)

    data = {}
    data['data'] = rows
    data['page'] = mw.getPage({'count':count,'tojs':'getLogs','p':p})
    return data

# 日志清空
@blueprint.route('/del_panel_logs', endpoint='del_panel_logs', methods=['POST'])
@panel_login_required
def del_panel_logs():
    db.session.query(Logs).filter(Logs.id > 0).delete()
    # db.session.execute('truncate table logs;')
    db.session.commit()
    mw.writeLog('面板设置', '面板操作日志已清空!')
    return mw.returnData(True, '面板操作日志已清空!')

# 系统审计日志列表
@blueprint.route('/get_audit_logs_files', endpoint='get_audit_logs_files', methods=['POST'])
@panel_login_required
def get_audit_logs_files():
    logs_file = adult_log.getAuditLogsFiles()
    return logs_file

# 系统审计日志列表
@blueprint.route('/get_audit_file', endpoint='get_audit_file', methods=['POST'])
@panel_login_required
def get_audit_file():
    name = request.form.get('log_name', '').strip()
    return adult_log.getAuditLogsName(name)









